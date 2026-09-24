$ErrorActionPreference = "Continue"
$repo = "C:\Users\chris\Math-To-Manim"
$mp4 = "$repo\media\videos\dzhanibekov_traitor_axis\720p15\TraitorAxis.mp4"
$out = "$repo\docs\showcase\assets\traitor-axis.gif"
$log = "$repo\runs\traitor_gif.log"

"START $(Get-Date -Format o)" | Out-File $log
ffmpeg -v error -i $mp4 -vf "fps=15,scale=680:-1:flags=lanczos,palettegen=stats_mode=diff" -y "$repo\runs\pal_traitor.png" 2>> $log
ffmpeg -v error -i $mp4 -i "$repo\runs\pal_traitor.png" -lavfi "fps=15,scale=680:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle" -y $out 2>> $log
"GIF_DONE $(Get-Date -Format o)" | Add-Content $log
