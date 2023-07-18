const express = require('express');
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const app = express();

// Create a mosaic from a grid of images
async function createMosaic(images, mosaicWidth, mosaicHeight) {
  // Create a blank canvas to draw the mosaic on
  const canvas = sharp({
    create: {
      width: mosaicWidth * imageWidth,
      height: mosaicHeight * imageHeight,
      channels: 4,
      background: { r: 0, g: 0, b: 0, alpha: 0 }
    }
  });

  // Draw each image onto the canvas at the correct position
  for (let y = 0; y < mosaicHeight; y++) {
    for (let x = 0; x < mosaicWidth; x++) {
      const image = images[y * mosaicWidth + x];
      canvas.composite([{ input: image, top: y * imageHeight, left: x * imageWidth }]);
    }
  }

  // Write the mosaic to a file
  await canvas.toFile('mosaic.png');
}

// Split a large image into a grid of smaller images
async function splitImageIntoGrid(sourceImage, numRows, numCols) {
  const image = sharp(sourceImage);
  const metadata = await image.metadata();
  const { width, height } = metadata;

  const cellWidth = Math.floor(width / numCols);
  const cellHeight = Math.floor(height / numRows);

  // Create the output directory if it doesn't exist
  const outputDir = 'output_images';
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir);
  }

  // Split the image into smaller images
  for (let row = 0; row < numRows; row++) {
    for (let col = 0; col < numCols; col++) {
      const x = col * cellWidth;
      const y = row * cellHeight;

      const outputPath = path.join(outputDir, `image_${row}_${col}.png`);

      await image
        .extract({ left: x, top: y, width: cellWidth, height: cellHeight })
        .toFile(outputPath);
    }
  }

  console.log(`Split ${sourceImage} into ${numRows} rows and ${numCols} columns.`);
}

// Endpoint to split the large image into a grid
app.get('/split-image', async (req, res) => {
  const sourceImage = 'path/to/source/image.jpg';
  const numRows = 3;
  const numCols = 4;

  await splitImageIntoGrid(sourceImage, numRows, numCols);

  res.send('Image split into grid.');
});

// Endpoint to create a mosaic from the grid of images
app.get('/create-mosaic', async (req, res) => {
  const mosaicWidth = 4;
  const mosaicHeight = 3;
  const images = [];

  // Assuming the grid of images is stored in the 'output_images' directory
  const gridDir = 'output_images';

  // Read the images from the grid directory
  for (let row = 0; row < mosaicHeight; row++) {
    for (let col = 0; col < mosaicWidth; col++) {
      const imageFile = path.join(gridDir, `image_${row}_${col}.png`);
      const imageBuffer = fs.readFileSync(imageFile);
      images.push(imageBuffer);
    }
  }

  await createMosaic(images, mosaicWidth, mosaicHeight);

  res.send('Mosaic created.');
});

// Start the server
app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
