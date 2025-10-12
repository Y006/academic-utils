# Force UTF-8 encoding
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Prompt for experiment name
$expName = Read-Host "Enter experiment name (e.g., exp1)"
$expDir = Join-Path "output" $expName
$saveDir = Join-Path $expDir "save_models"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Create directory structure
New-Item -ItemType Directory -Force -Path $expDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $expDir "logs") | Out-Null
New-Item -ItemType Directory -Force -Path $saveDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $saveDir "checkpoints") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $saveDir "current_best") | Out-Null

# Write config.yaml
$config = @"
model:
  name: unet

training:
  epochs: 100
  batch_size: 16
  learning_rate: 0.0005
  optimizer: adam
  weight_decay: 1e-5
  lr_scheduler: cosine
  gradient_clip_val: 1.0
  use_amp: true
  resume_from: ""

loss:
  type: mse

metrics:
  - psnr
  - ssim
  - mae

data:
  train_dataset: "./data/train"
  val_dataset: "./data/val"
  patch_size: 128

save:
  save_best_only: true
  checkpoint_dir: "./save_models/checkpoints"
"@
Set-Content -Path (Join-Path $expDir "config.yaml") -Value $config

# Write notes.md
$notes = @"
# Experiment Notes

- Name: $expName
- Created at: $timestamp
- Description: (Add your experiment notes here)
"@
Set-Content -Path (Join-Path $expDir "notes.md") -Value $notes

Write-Host "Output folder created at:" $expDir