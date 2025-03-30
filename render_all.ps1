# PowerShell script to render all scenes and combine them with ffmpeg
Write-Host "Starting to render QED animation scenes..." -ForegroundColor Green

# Define the scenes to render
$scenes = @(
    "Scene1_SpacetimeContext",
    "Scene2_ClassicalEM_to_Relativistic", 
    "Scene3_QEDLagrangian",
    "Scene4_FeynmanDiagram",
    "Scene5_Renormalization",
    "Scene6_Synthesis"
)

# Directory for rendered videos
$mediaDir = "media/videos/QEDGemini25/480p15"
$outputDir = "final_output"

# Create output directory if it doesn't exist
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir
}

# Create a file list for ffmpeg
$fileListPath = "$outputDir/file_list.txt"
if (Test-Path $fileListPath) {
    Remove-Item $fileListPath
}

# Render each scene
foreach ($scene in $scenes) {
    Write-Host "Rendering $scene..." -ForegroundColor Cyan
    
    # Run manim to render the scene
    python -m manim -pql QEDGemini25.py $scene
    
    # Check if the rendered file exists
    $renderedFile = "$mediaDir/$scene.mp4"
    if (Test-Path $renderedFile) {
        # Add to file list for ffmpeg
        Add-Content -Path $fileListPath -Value "file '$((Resolve-Path $renderedFile).Path)'"
        Write-Host "Successfully rendered $scene" -ForegroundColor Green
    } else {
        Write-Host "Failed to render $scene" -ForegroundColor Red
    }
}

# Combine videos using ffmpeg
Write-Host "Combining videos with ffmpeg..." -ForegroundColor Yellow
$outputFile = "$outputDir/QED_Complete_Animation.mp4"

# Check if ffmpeg is in PATH
$ffmpegPath = Get-Command ffmpeg -ErrorAction SilentlyContinue
if ($null -eq $ffmpegPath) {
    Write-Host "ffmpeg not found in PATH. Please install ffmpeg or add it to your PATH." -ForegroundColor Red
    exit 1
}

# Run ffmpeg to concatenate videos
ffmpeg -f concat -safe 0 -i $fileListPath -c copy $outputFile

if (Test-Path $outputFile) {
    Write-Host "Successfully created final video: $outputFile" -ForegroundColor Green
    
    # Open the final video
    Write-Host "Opening final video..." -ForegroundColor Cyan
    Start-Process $outputFile
} else {
    Write-Host "Failed to create final video" -ForegroundColor Red
} 