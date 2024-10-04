# Denoising
Google Dataset URI: https://drive.google.com/drive/folders/1aygMzSDdoq63IqSk-ly8cMq0_owup8UM

1. Download the dataset and the pre-trained model - run the commands from the root.
    ```bash
    # pretrained model
    chmod +x ./bin/download_pretrained.sh
    ./bin/download_pretrained.sh
    # open google dataset
    chmod +x ./Denoising/bin/unzip_dataset.sh
    ./Denoising/bin/unzip_dataset.sh
    chmod +x ./bin/download_dataset.sh
    ./bin/download_dataset.sh
    ```
2. [Train the network](network_trainer.ipynb)
3. [Validate the network](network_validation.ipynb)
