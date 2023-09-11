const express = require('express');
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');
const e = require('express');

const app = express();
app.use(express.json());


// Split a large image into a grid of smaller images
  async function splitImageIntoGrid(sourceImage, numRows, numCols) {
    try {
      const image = sharp(sourceImage);
      const metadata = await image.metadata();
      const { width, height } = metadata;
  
      const cellWidth = Math.floor(width / numCols);
      const cellHeight = Math.floor(height / numRows);

      console.log(`Cell Width: ${cellWidth}, Cell Height: ${cellHeight}`);
    
      // console.log(`Source image dimensions: ${width}x${height}`);
      // console.log(`Cell dimensions: ${cellWidth}x${cellHeight}`);


      // Create the output directory if it doesn't exist
      const outputDir = 'images/cells/charger66';
      /*
      if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir);
      }
      */
  
      // Split the image into smaller images
      for (let row = 0; row < numRows; row++) {
        for (let col = 0; col < numCols; col++) {
          const x = Math.floor(col * cellWidth);
          const y = Math.floor(row * cellHeight);
  
          console.log(`Row: ${row}, Col: ${col}, x: ${x}, y: ${y}, cellWidth: ${cellWidth}, cellHeight: ${cellHeight}`);

          const outputPath = path.join(outputDir, `image_${row}_${col}.jpg`);
          console.log(`Output path: ${outputPath}`);
          console.log(`Extracting cell at (${x}, ${y}) with width ${cellWidth} and height ${cellHeight}`);

          /*
          try {
            const extractedImage = image.extract({ left: x, top: y, width: cellWidth, height: cellHeight });
            const buffer = await extractedImage.toBuffer();
            // await fs.writeFile(outputPath, buffer);
            console.log(`Saved image_${row}_${col}.png`);
          } catch (error) {
            console.error('Error while extracting and saving image:', error);
          }
          */


          await sharp(sourceImage)
            .extract({ left: x, top: y, width: cellWidth, height: cellHeight })
            .toFile(outputPath);
          

        /*
          await image
          .extract({ left: x, top: y, width: cellWidth, height: cellHeight })
          .jpeg.toString('base64');
        */
        }
        
      }
  
      console.log(`Split ${sourceImage} into ${numRows} rows and ${numCols} columns.`);
    } catch (error) {
      console.error('Error while splitting the image:', error);
    }
  }



// TODO: for non-zero padding, gridlines are not drawn correctly.  Need to fix this.
async function createMosaic(gridData, cellType, padding=0) {
  const mosaicRows = gridData[0].length;
  const mosaicCols = gridData[0][0].length;
  // const mosaicRows = 5;
  // const mosaicCols = 5;
  const gridLineWidth = 1; // width of the grid lines in pixels
  // const baseDir = 'images/cells/charger66';
  const baseDir = 'images/cells/fna_violo_patch/violo_patch';

  console.log(`Mosaic Rows: ${mosaicRows}, Mosaic Cols: ${mosaicCols}, Base Dir: ${baseDir}, Grid Data in CREATE-MOSAIC: ${JSON.stringify(gridData)}`);

  // Find the largest image dimensions in the grid
  let grid = 0;
  let maxCellWidth = 0;
  let maxCellHeight = 0;
  for (let row = 0; row < mosaicRows; row++) {
    for (let col = 0; col < mosaicCols; col++) {
	  if (typeof(gridData[grid][row][col]) === 'undefined') {
		continue;
	  }
      const imageFile = `${baseDir}/${gridData[grid][row][col]}`;
      if (!fs.existsSync(imageFile)) { 
        continue; 
      } 
      const { width, height } = await getImageDimensions(imageFile);
      maxCellWidth = Math.max(maxCellWidth, width);
      maxCellHeight = Math.max(maxCellHeight, height);
    }
  }
  // adjust maxCellWidth and maxCellHeight to include padding
  maxCellWidth = Math.ceil(maxCellWidth * (1 + padding/100));
  maxCellHeight = Math.ceil(maxCellHeight * (1 + padding/100));
  const canvasWidth =  Math.ceil((mosaicCols *  maxCellWidth) + (gridLineWidth * (mosaicCols + 1)));
  const canvasHeight = Math.ceil((mosaicRows * maxCellHeight) + (gridLineWidth * (mosaicRows + 1)));
  console.log(`Max Cell Width: ${maxCellWidth}, Max Cell Height: ${maxCellHeight}, Canvas Width: ${canvasWidth}, Canvas Height: ${canvasHeight}`);


  const compositeOperations = [];

  // Create a blank canvas to draw the mosaic on
  let canvas = sharp({
    create: {
      width: canvasWidth,
      height: canvasHeight,
      channels: 4,
      background: { r: 255, g: 255, b: 255, alpha: 1 } // white background
    }
  });

  // Create a blank image to use as the background for any empty cells
  (async () => {
    // const blankImageBuffer = await createBlankImage(maxCellWidth, maxCellHeight, { r: 0, g: 0, b: 0 }); // Black image

    // If you wanted to save it to a file:
    // await sharp(blankImageBuffer).toFile('blankImage.png');
  })();

  // Draw each image onto the canvas at the correct position with padding
  for (let row = 0; row < mosaicRows; row++) {
    for (let col = 0; col < mosaicCols; col++) {
      const imageFile = `${baseDir}/${gridData[grid][row][col]}`;

      const xOffset = col * (maxCellWidth + gridLineWidth) + gridLineWidth;
      const yOffset = row * (maxCellHeight + gridLineWidth) + gridLineWidth;

      if (typeof(gridData[grid][row][col]) === 'undefined' || !fs.existsSync(imageFile)) { 
        const blankImageWithBackground = await createBlankImage(maxCellWidth, maxCellHeight, { r: 0, g: 0, b: 0 }); // Black image; 
        compositeOperations.push({ input: blankImageWithBackground, top: yOffset, left: xOffset });
        console.log(`Row: ${row}, Col: ${col}, xOffset: ${xOffset}, yOffset: ${yOffset}, width: ${maxCellWidth}, height: ${maxCellHeight}, imageFile: BLANK`);
      } else {
        const { width, height } = await getImageDimensions(imageFile);

        // Create a white background for each image
        const imageWithBackground = await sharp(imageFile)
          .extend({
            top: Math.ceil((maxCellHeight - height) / 2),
            bottom: Math.ceil((maxCellHeight - height) / 2),
            left: Math.ceil((maxCellWidth - width) / 2),
            right: Math.ceil((maxCellWidth - width) / 2),
            background: { r: 5, g: 5, b: 5, alpha: 1 }
          })
          .toBuffer();

          compositeOperations.push({ input: imageWithBackground, top: yOffset, left: xOffset });
          console.log(`Row: ${row}, Col: ${col}, xOffset: ${xOffset}, yOffset: ${yOffset}, width: ${width}, height: ${height}, imageFile: ${imageFile}`);
      }
    }
  }

  // composite all images once
  canvas = await canvas.composite(compositeOperations);

  // Write the mosaic to a file
  await canvas.toFile(`images/mosaics/grid-${cellType}-${grid}.png`);
}

async function getImageDimensions(imageFilePath) {
  try {
    const metadata = await sharp(imageFilePath).metadata();
    return { width: metadata.width, height: metadata.height };
  } catch (error) {
    console.error('Error while getting image dimensions:', error);
    return { width: 0, height: 0 };
  }
}


function getGridData() {
  const gridData = [
    [
      [
        "fld-q196-145867-1434,449-42,53-mast_cell.png",
        "fld-q196-194606-1921,1439-44,46-mast_cell.png",
        "fld-q196-197650-1024,283-138,204-mast_cell.png",
        "fld-q310-212447-793,820-50,50-mast_cell.png",
        "fld-q310-212469-137,712-51,52-mast_cell.png",
      ],
      [
        "fld-q310-250901-282,730-55,56-mast_cell.png",
        "fld-q310-354695-1044,889-62,57-mast_cell.png",
        "fld-q310-354705-1593,484-61,68-mast_cell.png",
        "fld-q310-86350-1132,807-61,57-mast_cell.png",
        "fld-q548-130952-1890,63-52,55-mast_cell.png"
      ],
      [
        "fld-q548-130997-1118,363-62,64-mast_cell.png",
        "fld-q548-131433-1561,500-45,43-mast_cell.png",
      ],
    ]
  ];
  
  const rbcGridData = [
    [
      [
        "fld-q196-115217-466,937-28,24-nRBC.png",
        "fld-q310-42129-1571,364-28,28-nRBC.png",
        "fld-q310-42132-1269,881-27,24-nRBC.png",
        "fld-q310-42132-2196,1009-26,27-nRBC.png",
        "fld-q310-42132-2243,540-29,28-nRBC.png",
      ],
      [
        "fld-q310-47346-1184,1809-23,24-nRBC.png",
        "fld-q310-47346-1436,1036-26,27-nRBC.png",
        "fld-q310-47346-1585,379-21,21-nRBC.png",
        "fld-q310-47346-1871,1289-25,25-nRBC.png",
        "fld-q310-47346-2116,618-19,23-nRBC.png",
      ],
      [
        "fld-q310-47346-2404,974-25,27-nRBC.png",
        "fld-q310-47346-396,1041-24,23-nRBC.png",
        "fld-q310-47346-776,719-27,26-nRBC.png",
        "fld-q310-47347-1201,103-24,23-nRBC.png",
        "fld-q310-47347-1490,1761-23,24-nRBC.png",
      ],
      [
        "fld-q310-47347-1593,462-26,22-nRBC.png",
        "fld-q310-47347-1822,1108-23,28-nRBC.png",
        "fld-q310-47347-23,1264-23,20-nRBC.png",
        "fld-q310-47347-2378,1216-24,23-nRBC.png",
        "fld-q310-47347-562,1604-25,27-nRBC.png",
      ],
      [
        "fld-q310-47347-724,1206-23,25-nRBC.png",
        "fld-q310-55407-122,359-27,25-nRBC.png",
        "fld-q310-55407-1307,1656-29,29-nRBC.png",
        "fld-q310-55407-1644,1895-23,26-nRBC.png",
        "fld-q310-55407-2565,1546-26,28-nRBC.png",
      ],
    ],
    [
      [
        "fld-q310-55409-1099,287-29,22-nRBC.png",
        "fld-q310-62157-2086,96-28,30-nRBC.png",
        "fld-q310-62157-2290,912-27,32-nRBC.png",
      ],
    ],
  ];
  return gridData;
}

// Generate a blank, in-memory image with a specific color
async function createBlankImage(width, height, color) {
  // Ensure color has an alpha channel, defaulting to 1 (fully opaque)
  if (!color.alpha) {
    color.alpha = 1;
  }

  const imageBuffer = await sharp({
    create: {
      width: width,
      height: height,
      channels: 4,
      background: color
    }
  }).png().toBuffer(); // You can change this to .jpeg() if you prefer

  return imageBuffer;
}


// Endpoint to create a mosaic from the grid of images
app.get('/create-mosaic', async (req, res) => {
  // const gridData = req.body;
  const padding = req.query.padding || 0; // padding for each grid cell, as a percentage of the cell size
 

/*
  const mosaicRows = 5;
  const mosaicCols = 5;

  const gridData = Array.from({length: mosaicRows}, () => Array(mosaicCols).fill(''));
  for (let row = 0; row < mosaicRows; row++) {
    for (let col = 0; col < mosaicCols; col++) {
      gridData[row][col] = `image_${row}_${col}.jpg`;
	    // console.log("filename: " + gridData[row][col]);
	  }
  }
*/
  const gridData = getGridData();

  console.log(`Grid Data: ${JSON.stringify(gridData)}`);
  console.log(`Grid Data AFTER STRINGIFY: ${JSON.stringify(gridData)}`);

  if (!Array.isArray(gridData) || gridData.some(row => !Array.isArray(row))) {
    res.status(400).send('Invalid grid data format. Please provide a structured representation of the grid.');
    return;
  }

  try {
    await createMosaic(gridData, "mast" , padding);
    res.send('Mosaic created.');
  } catch (error) {
    console.error('Error creating mosaic:', error);
    res.status(500).send('Error creating mosaic.');
  }
});

// Endpoint to split the large image into a grid
app.get('/split-image', async (req, res) => {
    const sourceImage = 'images/whole/charger66.jpg';
    const numRows = 5;
    const numCols = 8;
  
    await splitImageIntoGrid(sourceImage, numRows, numCols);
  
    res.send('Image split into grid.');
  });


// Endpoint to convert a png image to dicom via graphicsmagick
app.get('/convert-png-to-dicom', async (req, res) => {
	  const sourceImage = 'images/whole/charger66.jpg';
	  const dicomFile  = 'images/whole/charger66.dcm';

	  const gm = require('gm').subClass({imageMagick: true});
	  gm(sourceImage)
  		.setFormat('dicom')
  		.write(dicomFile, function (err) {
    		if (!err) console.log('done');
		});
	});


// Start the server
app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
