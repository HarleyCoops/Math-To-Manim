$ErrorActionPreference = "Continue"
$repo = "C:\Users\chris\Math-To-Manim"
$run = "$repo\runs\mythos\20260710-015439-the-cube-of-everything-one-continuous-3d-take-on"
$mp4 = "$run\FourConstantsVacuumWoundJourney.mp4"
$log = "$run\gifs.log"

"START $(Get-Date -Format o)" | Out-File $log

# Full-length showcase GIF (480px, 10fps)
ffmpeg -v error -i $mp4 -vf "fps=10,scale=480:-1:flags=lanczos,palettegen=stats_mode=diff" -y "$run\pal_full.png" 2>> $log
ffmpeg -v error -i $mp4 -i "$run\pal_full.png" -lavfi "fps=10,scale=480:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle" -y "$run\four_constants_full.gif" 2>> $log
"FULL_DONE $(Get-Date -Format o)" | Add-Content $log

# Highlight reel (light cone, cube, log elevator, canyon, glows)
ffmpeg -v error -i $mp4 -filter_complex "[0:v]trim=36:50,setpts=PTS-STARTPTS[a];[0:v]trim=152:170,setpts=PTS-STARTPTS[b];[0:v]trim=298:314,setpts=PTS-STARTPTS[c];[0:v]trim=385:400,setpts=PTS-STARTPTS[d];[0:v]trim=429:436.5,setpts=PTS-STARTPTS[e];[a][b][c][d][e]concat=n=5:v=1:a=0[v]" -map "[v]" -y "$run\highlights.mp4" 2>> $log
ffmpeg -v error -i "$run\highlights.mp4" -vf "fps=9,scale=420:-1:flags=lanczos,palettegen=stats_mode=diff" -y "$run\pal_hl.png" 2>> $log
ffmpeg -v error -i "$run\highlights.mp4" -i "$run\pal_hl.png" -lavfi "fps=9,scale=420:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle" -y "$run\four_constants_highlights.gif" 2>> $log
"HL_DONE $(Get-Date -Format o)" | Add-Content $log
