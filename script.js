import fs from "fs/promises";
import path from "path";
import sharp from "sharp";
import { fileURLToPath } from "url";
import { dirname } from "path";
import { Worker, isMainThread, parentPort, workerData } from "worker_threads";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// **Find Center of Non-Transparent Area**
async function findCenter(imagePath) {
    const image = sharp(imagePath);
    const metadata = await image.metadata();
    const { width, height } = metadata;
    return { centerX: Math.floor(width / 2), centerY: Math.floor(height / 2) };
}

// **Calculate Zoom Factor Based on Margins**
async function calculateZoom(imagePath, finalSize, margins, applyMargins) {
    if (!applyMargins) return 1.0; // No zoom if margins are disabled

    const image = sharp(imagePath);
    const metadata = await image.metadata();
    const { width, height } = metadata;

    const [top, bottom, left, right] = margins;
    const availableWidth = finalSize[0] - (left + right);
    const availableHeight = finalSize[1] - (top + bottom);

    return Math.min(availableWidth / width, availableHeight / height);
}

// **Scale Image Based on Zoom Factor**
async function scaleImage(imagePath, zoomFactor) {
    if (zoomFactor === 1.0) return imagePath; // No resizing required
    const image = sharp(imagePath);
    const metadata = await image.metadata();
    return await image.resize(Math.floor(metadata.width * zoomFactor), Math.floor(metadata.height * zoomFactor)).toBuffer();
}

// **Center Image with or without Margins**
async function centerImage(imagePath, finalSize, margins, applyMargins) {
    const { centerX, centerY } = await findCenter(imagePath);
    const [top, bottom, left, right] = applyMargins ? margins : [0, 0, 0, 0];

    const dx = (finalSize[0] - left - right) / 2 - centerX + left;
    const dy = (finalSize[1] - top - bottom) / 2 - centerY + top;

    return { dx: Math.floor(dx), dy: Math.floor(dy) };
}


// **Background Canvas Creation with Custom Color**
async function createCanvas(finalSize, bgColor) {
    return await sharp({
        create: {
            width: finalSize[0],
            height: finalSize[1],
            channels: 3,
            background: bgColor, // Use custom background color
        },
    }).toBuffer();
}

// **Merge Images on Custom Background**
async function processBackground(backgroundImage, dx, dy, finalSize, bgColor) {
    const canvas = await createCanvas(finalSize, bgColor);
    return await sharp(canvas).composite([{ input: backgroundImage, left: dx, top: dy }]).toBuffer();
}
// **Process Image Pair (Background + Transparent)**
async function processImagePair(inputFolder, outputFolder, bgFile, noBgFile, margins, applyMargins, bgColor) {
    try {
        await fs.mkdir(outputFolder, { recursive: true });

        const imgWithBgPath = path.join(inputFolder, bgFile);
        const imgNoBgPath = path.join(inputFolder, noBgFile);

        const finalSize = [(await sharp(imgNoBgPath).metadata()).width, (await sharp(imgNoBgPath).metadata()).height];

        const processedBg = await processBackground(await sharp(imgWithBgPath).toBuffer(), 0, 0, finalSize, bgColor);
        await sharp(processedBg).toFile(path.join(outputFolder, bgFile));

        console.log(`✅ Processed: ${bgFile} | Background Color: rgb(${bgColor.r}, ${bgColor.g}, ${bgColor.b})`);
    } catch (error) {
        console.error(`❌ Error processing ${bgFile}: ${error.message}`);
    }
}
// **Process Images in All Folders**
async function processImagesInFolders(inputRoot, outputRoot, margins, applyMargins, maxThreads, bgColor) { // bgColor add karyo
    const subfolders = (await fs.readdir(inputRoot)).filter((folder) => 
        fs.stat(path.join(inputRoot, folder)).then((s) => s.isDirectory())
    );

    const workerPool = [];
    for (const subfolder of subfolders) {
        const inputFolder = path.join(inputRoot, subfolder);
        const outputFolder = path.join(outputRoot, subfolder);
        await fs.mkdir(outputFolder, { recursive: true });

        const allFiles = await fs.readdir(inputFolder);
        const categories = ["R", "W", "Y"];

        for (const category of categories) {
            const bgImages = allFiles.filter((f) => f.startsWith(`${subfolder}-${category}-`) && f.endsWith(".png"));
            const noBgImages = allFiles.filter((f) => f.startsWith(`${subfolder}-${category}A-`) && f.endsWith(".png"));

            for (const bgFile of bgImages) {
                const correspondingNoBg = bgFile.replace(`-${category}-`, `-${category}A-`);
                if (noBgImages.includes(correspondingNoBg)) {
                    workerPool.push(
                        new Promise((resolve, reject) => {
                            const worker = new Worker(__filename, {
                                workerData: { 
                                    inputFolder, 
                                    outputFolder, 
                                    bgFile, 
                                    correspondingNoBg, 
                                    margins, 
                                    applyMargins, 
                                    bgColor  // 🎨 **bgColor pass karyo**
                                },
                            });
                            worker.on("message", resolve);
                            worker.on("error", reject);
                        })
                    );
                }
            }
        }
    }

    await Promise.all(workerPool);
}

// **Worker Thread Execution**
if (!isMainThread) {
    processImagePair(
        workerData.inputFolder, 
        workerData.outputFolder, 
        workerData.bgFile, 
        workerData.correspondingNoBg, 
        workerData.margins, 
        workerData.applyMargins, 
        workerData.bgColor  // 🎨 **bgColor pass karyo**
    )
    .then(() => parentPort.postMessage("done"))
    .catch((err) => parentPort.postMessage(`error: ${err.message}`));
}

// **Main Execution (CLI Arguments)**
if (isMainThread) {
    if (process.argv.length !== 10) { // 🌟 RGB ne ek j argument banavyo
        console.log("Usage: node script.js <input_folder> <output_folder> <top_margin> <right_margin> <bottom_margin> <left_margin> <apply_margins: 0 or 1> <max_threads> <bg_color: R,G,B>");
        process.exit(1);
    }

    const [inputFolder, outputFolder, top, right, bottom, left, applyMargins, maxThreads, bgColorStr] = process.argv.slice(2);
    const margins = [parseInt(top), parseInt(bottom), parseInt(left), parseInt(right)];
    const applyMarginsBool = Boolean(parseInt(applyMargins));
    const threadCount = Math.max(1, parseInt(maxThreads));
    
    // 🎨 **RGB color parse karva**
    const bgColor = { r: parseInt(bgRed), g: parseInt(bgGreen), b: parseInt(bgBlue) };


    console.log(`🎨 Custom Background Color Set: rgb(${bgColor.r}, ${bgColor.g}, ${bgColor.b})`);
    
    processImagesInFolders(inputFolder, outputFolder, margins, applyMarginsBool, threadCount, bgColor);
}
