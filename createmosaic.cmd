curl -X POST -H "Content-Type: application/json" -d '{
  "gridData": [
    ["image_0_0.jpg", "image_0_1.jpg", "image_0_2.jpg"],
    ["image_1_0.jpg", "image_1_1.jpg", "image_1_2.jpg"],
    ["image_2_0.jpg", "image_2_1.jpg", "image_2_2.jpg"]
  ]
}' http://localhost:3000/create-mosaic
