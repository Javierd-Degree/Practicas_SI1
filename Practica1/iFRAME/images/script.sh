img_path=./
img_results=./results
mkdir -p $img_results
for img in ${img_path}/*;
    do 
    convert -negate $img ${img_results}/${img#./*};
done
