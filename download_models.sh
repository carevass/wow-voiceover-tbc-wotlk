#!/bin/bash
# setup folders for dependencies and download the base xtts and rvc model files

# Create folder structure
mkdir -p ./inputs/fine_tuned/base
mkdir -p ./inputs/fine_tuned/_rvc/indices
mkdir -p ./inputs/fine_tuned/_rvc/models/ckpt/rmvpe
mkdir -p ./inputs/fine_tuned/_rvc/models/ckpt/hubert
mkdir -p ./inputs/fine_tuned/_rvc/weights
mkdir -p ./inputs/voices

# Download XTTS Weights if missing
if [ ! -f "./inputs/fine_tuned/base/model.pth" ]; then
    echo "Downloading XTTS weights..."
    wget -O ./inputs/fine_tuned/base/model.pth https://huggingface.co/coqui/XTTS-v2/resolve/2c2f9f1e633b0135c41c96c843ebfe52db1d7aa4/model.pth
    wget -O ./inputs/fine_tuned/base/vocab.json https://huggingface.co/coqui/XTTS-v2/resolve/2c2f9f1e633b0135c41c96c843ebfe52db1d7aa4/vocab.json
    wget -O ./inputs/fine_tuned/base/dvae.pth https://huggingface.co/coqui/XTTS-v2/resolve/2c2f9f1e633b0135c41c96c843ebfe52db1d7aa4/dvae.pth
    wget -O ./inputs/fine_tuned/base/config.json https://huggingface.co/coqui/XTTS-v2/resolve/main/config.json
    wget -O ./inputs/fine_tuned/base/speakers_xtts.pth https://huggingface.co/coqui/XTTS-v2/resolve/main/speakers_xtts.pth
fi

# Download RVC components
if [ ! -f "./inputs/fine_tuned/_rvc/models/ckpt/rmvpe/rmvpe.pt" ]; then
    echo "Downloading RMVPE..."
    wget -O ./inputs/fine_tuned/_rvc/models/ckpt/rmvpe/rmvpe.pt https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/rmvpe.pt
fi

if [ ! -f "./inputs/fine_tuned/_rvc/models/ckpt/hubert/hubert_base.pt" ]; then
  echo "Downloading Hubert..."
  wget -O ./inputs/fine_tuned/_rvc/models/ckpt/hubert/hubert_base.pt https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/hubert_base.pt
fi
