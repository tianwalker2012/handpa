# Converting the source from JPEG to PNG - if necessary
convert $1  my_src_image.png
 
 
# Option A
#  - Requires a temporary intermediate file
#  - Drill more than 10 might result in poor results
DRILL=5
convert my_src_image.png \( +clone -fx "p{0,0}" \) -compose Difference -composite -modulate 100,0  +matte temp_image_xzy.png
convert temp_image_xzy.png -bordercolor white -border 1x1 -matte -fill none -fuzz $DRILL% -draw "matte 1,1 floodfill" -shave 1x1 temp_image_xzy.png
convert temp_image_xzy.png -channel matte -separate +matte temp_image_xzy.png
convert temp_image_xzy.png -negate -blur 0x1 temp_image_xzy.png
composite -compose CopyOpacity temp_image_xzy.png my_src_image.png final_image_option_A.png
 
# Remove the temp file 
rm -f temp_image_xzy.png
 
# below instruction is optional
composite -compose Dst_Over -tile pattern:checkerboard final_image_option_A.png final_image_option_A_check.png
 
# //End of Option A
 
 
 
# Option B
#  - Requires a temporary intermediate file
#  - Drill more than 10 might result in poor results
DRILL=5
convert my_src_image.png \( +clone -fx "p{0,0}" \) -compose Difference -composite -modulate 100,0 +matte temp_image_xzy.png
convert -fuzz $DRILL% -transparent black temp_image_xzy.png temp_image_xzy.png
convert temp_image_xzy.png -channel matte -separate +matte temp_image_xzy.png
convert temp_image_xzy.png -negate -blur 0x1 temp_image_xzy.png
composite -compose CopyOpacity temp_image_xzy.png my_src_image.png final_image_option_B.png
 
# Remove the temp file 
rm -f temp_image_xzy.png
 
# below instruction is optional
composite -compose Dst_Over -tile pattern:checkerboard final_image_option_B.png final_image_option_B_check.png
 
# //End of Option B
 
 
 
# Option C
#  - Drill more than 10 might result in poor results
DRILL=5
convert my_src_image.png -bordercolor white -border 1x1 -matte -fill none -fuzz $DRILL% -draw "matte 1,1 floodfill" -shave 1x1 final_image_option_C.png
 
# below instruction is optional
composite -compose Dst_Over -tile pattern:checkerboard final_image_option_C.png final_image_option_C_check.png
 
# //End of Option C
 
 
 
# Option D
#  - Drill more than 10 might result in poor results
DRILL=5
convert -fuzz $DRILL% -transparent white my_src_image.png final_image_option_D.png
 
# below instruction is optional
composite -compose Dst_Over -tile pattern:checkerboard final_image_option_D.png final_image_option_D_check.png
 
# //End of Option D

