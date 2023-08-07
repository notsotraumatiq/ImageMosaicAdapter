const express = require('express');
const sharp = require('sharp');
const fs = require('fs/promises');
const path = require('path');

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


async function createMosaic(gridData) {
  const mosaicHeight = gridData.length;
  const mosaicWidth = gridData[0].length;
  // const baseDir = 'images/cells/charger66';
  const baseDir = 'images/cells/fna_viola_patch/viola_patch';

  console.log(`Mosaic Height: ${mosaicHeight}, Mosaic Width: ${mosaicWidth}, Base Dir: ${baseDir}, Grid Data: ${gridData}`);

  // Find the largest image dimensions in the grid
  let maxWidth = 0;
  let maxHeight = 0;
  for (let row = 0; row < mosaicHeight; row++) {
    for (let col = 0; col < mosaicWidth; col++) {
      const imageFile = `${baseDir}/${gridData[row][col]}`;
      const { width, height } = await getImageDimensions(imageFile);
      maxWidth = Math.max(maxWidth, width);
      maxHeight = Math.max(maxHeight, height);
    }
  }

  const compositeOperations = [];

  // Create a blank canvas to draw the mosaic on
  let canvas = sharp({
    create: {
      width: Math.ceil(mosaicWidth * maxWidth),
      height: Math.ceil(mosaicHeight * maxHeight),
      channels: 4,
      background: { r: 0, g: 0, b: 0, alpha: 0 }
    }
  });

  // Draw each image onto the canvas at the correct position with padding
  for (let row = 0; row < mosaicHeight; row++) {
    for (let col = 0; col < mosaicWidth; col++) {
      const imageFile = `${baseDir}/${gridData[row][col]}`;
      const { width, height } = await getImageDimensions(imageFile);
      const xOffset = col * maxWidth + Math.ceil((maxWidth - width) / 2);
      const yOffset = row * maxHeight + Math.ceil((maxHeight - height) / 2);

      console.log(`Row: ${row}, Col: ${col}, xOffset: ${xOffset}, yOffset: ${yOffset}, width: ${width}, height: ${height}, imageFile: ${imageFile}`);
      compositeOperations.push({ input: imageFile, top: yOffset, left: xOffset });
    }
  }

  // composite all images once
  canvas = await canvas.composite(compositeOperations);

  // Write the mosaic to a file
  await canvas.toFile('images/mosaics/charger66mosaic.png');
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

// Endpoint to create a mosaic from the grid of images
app.get('/create-mosaic', async (req, res) => {
  // const gridData = req.body;
 
  const mosaicHeight = 5;
  const mosaicWidth = 5;

  /*
  const gridData = Array.from({length: mosaicHeight}, () => Array(mosaicWidth).fill(''));
  for (let row = 0; row < mosaicHeight; row++) {
    for (let col = 0; col < mosaicWidth; col++) {
      gridData[row][col] = `image_${row}_${col}.jpg`;
	  // console.log("filename: " + gridData[row][col]);
	}
  }
*/
  const gridData = getGridData();

  console.log(`Grid Data: ${JSON.stringify(gridData)}`);

  if (!Array.isArray(gridData) || gridData.some(row => !Array.isArray(row))) {
    res.status(400).send('Invalid grid data format. Please provide a structured representation of the grid.');
    return;
  }

  try {
    await createMosaic(gridData);
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
