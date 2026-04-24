#!/bin/bash
set -e

echo "=========================================="
echo "乡村老师助教系统 - 模型下载脚本"
echo "=========================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_PYTHON="$PROJECT_DIR/.conda/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment Python not found at $VENV_PYTHON"
    echo "Please ensure the conda environment is set up correctly."
    exit 1
fi

echo "Using Python: $VENV_PYTHON"

mkdir -p "$PROJECT_DIR/models"

echo ""
echo "Step 1: Installing required packages..."
$VENV_PYTHON -m pip install huggingface_hub -q

echo ""
echo "=========================================="
echo "Available models to download:"
echo "=========================================="
echo "1. qwen       - Qwen2.5-7B-Instruct (约14GB)"
echo "2. sensevoice - SenseVoice 语音识别 (约2GB)"
echo "3. cosyvoice  - CosyVoice 语音合成 (约1GB)"
echo "4. embedding  - paraphrase-multilingual-MiniLM-L12-v2 (约500MB)"
echo "5. all        - Download all models"
echo ""

read -p "请选择要下载的模型 (1-5): " choice

case $choice in
    1) models="qwen" ;;
    2) models="sensevoice" ;;
    3) models="cosyvoice" ;;
    4) models="embedding" ;;
    5) models="all" ;;
    *) echo "Invalid choice"; exit 1 ;;
esac

download_model() {
    local model_key=$1
    local model_name=$2
    local output_path="$PROJECT_DIR/models/$model_key"

    echo ""
    echo "----------------------------------------"
    echo "Downloading $model_name..."
    echo "Output: $output_path"
    echo "----------------------------------------"

    if [ -d "$output_path" ] && [ "$(ls -A $output_path)" ]; then
        read -p "Model already exists. Re-download? (y/N): " confirm
        if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
            echo "Skipping $model_key"
            return 0
        fi
    fi

    echo "Downloading (this may take a while for large models)..."
    $VENV_PYTHON -c "
from huggingface_hub import snapshot_download
print(f'Downloading {model_name}...')
snapshot_download(
    repo_id='$model_name',
    local_dir='$output_path',
    local_dir_use_symlinks=False,
    resume_download=True
)
print('Download complete!')
"
}

if [ "$models" == "all" ]; then
    download_model "embedding" "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    download_model "qwen" "Qwen/Qwen2.5-7B-Instruct"
    download_model "sensevoice" "iic/SenseVoiceSmall"
    download_model "cosyvoice" "FunAudioLLM/CosyVoice-300M"
else
    case $models in
        qwen)
            download_model "qwen" "Qwen/Qwen2.5-7B-Instruct"
            ;;
        sensevoice)
            download_model "sensevoice" "iic/SenseVoiceSmall"
            ;;
        cosyvoice)
            download_model "cosyvoice" "FunAudioLLM/CosyVoice-300M"
            ;;
        embedding)
            download_model "embedding" "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            ;;
    esac
fi

echo ""
echo "=========================================="
echo "Download complete! Checking status..."
echo "=========================================="

$VENV_PYTHON "$SCRIPT_DIR/manage_models.py" --check

echo ""
echo "To start the model services, run:"
echo "  $VENV_PYTHON $SCRIPT_DIR/start_all.py"
