x_range_callback = """
var start = cb_obj.start;
var end = cb_obj.end;
var width = end - start;
var threshold = %f * width;     // threshold factor is set from python-side configuration
var intron_alpha = %f;          // alpha value is set from python-side configuration

// iterate over each intron
var data = source.data;
for (i=0; i<data["x"].length; i++)
{
    // if the screen-space width is large enough, make the intron visible
    if(data["width"][i] >= threshold)
        data["alpha"][i] = intron_alpha;
    else
    // otherwise, make the intron fully transparent
        data["alpha"][i] = 0;
}

source.change.emit();
"""