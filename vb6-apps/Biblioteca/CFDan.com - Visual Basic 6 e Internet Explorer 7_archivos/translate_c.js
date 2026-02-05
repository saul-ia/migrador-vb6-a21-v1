/**
 * Generates a browser-specific Flash tag. Create a new instance, set whatever
 * properties you need, then call either toString() to get the tag as a string, or
 * call write() to write the tag out.
 */

/**
 * Creates a new instance of the FlashTag.
 * src: The path to the SWF file.
 * width: The width of your Flash content.
 * height: the height of your Flash content.
 */
function FlashTag(src, width, height)
{
    this.src       = src;
    this.width     = width;
    this.height    = height;
    this.version   = '7,0,14,0';
    this.id        = null;
    this.bgcolor   = null;//'ffffff';
    this.flashVars = null;
	this.wmode	   = null;
}

/**
 * Sets the Flash version used in the Flash tag.
 */
FlashTag.prototype.setVersion = function(v)
{
    this.version = v;
}

/**
 * Sets the ID used in the Flash tag.
 */
FlashTag.prototype.setId = function(id)
{
    this.id = id;
}

/**
 * Sets the background color used in the Flash tag.
 */
FlashTag.prototype.setBgcolor = function(bgc)
{
    this.bgcolor = bgc;
}

/**
 * Sets any variables to be passed into the Flash content. 
 */
FlashTag.prototype.setFlashvars = function(fv)
{
    this.flashVars = fv;
}

/**
 * Get the Flash tag as a string. 
 */
FlashTag.prototype.toString = function()
{
    var ie = (navigator.appName.indexOf ("Microsoft") != -1) ? 1 : 0;
    var flashTag = new String();
	var paramList = ['scale','salign',['quality','high']];
    if(ie)
    {
        flashTag += '<object classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" ';
        if (this.id != null)
        {
            flashTag += 'id="'+this.id+'" ';
        }
        flashTag += 'codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version='+this.version+'" ';
        flashTag += 'width="'+this.width+'" ';
        flashTag += 'height="'+this.height+'">';
        flashTag += '<param name="movie" value="'+this.src+'"/>';
		for(var i=0;i<paramList.length;i++)
		{
			var param = paramList[i];
			if( typeof(param) == "object" ) { param = paramList[i][0]; if( this[param] == null ) this[param] = paramList[i][1]; }
			if( this[param] != null ) flashTag += '<param name="'+param+'" value="'+this[param]+'"/>';
		}
		if(this.bgcolor != null) flashTag += '<param name="bgcolor" value="#'+this.bgcolor+'"/>';
        if(this.flashVars != null)
        {
            flashTag += '<param name="flashvars" value="'+this.flashVars+'"/>';
        }
		if(this.wmode != null)
		{
			flashTag += '<param name="wmode" value="'+this.wmode+'" />';
		}
        flashTag += '</object>';
    }
    else
    {
        flashTag += '<embed src="'+this.src+'" ';
        flashTag += 'quality="high" '; 
        if(this.bgcolor != null) flashTag += 'bgcolor="#'+this.bgcolor+'" ';
        flashTag += 'width="'+this.width+'" ';
        flashTag += 'height="'+this.height+'" ';
        flashTag += 'type="application/x-shockwave-flash" ';
		for(var i=0;i<paramList.length;i++)
		{
			param = paramList[i];
			if( typeof(param) == "object" ) { param = paramList[i][0]; if( this[param] == null ) this[param] = paramList[i][1]; }
			if( this[param] != null ) flashTag += param+'="'+this[param]+'" ';
		}
        if (this.flashVars != null)
        {
            flashTag += 'flashvars="'+this.flashVars+'" ';
        }
		if(this.wmode != null)
		{
			flashTag += 'wmode="'+this.wmode+'" ';
		}
        if (this.id != null)
        {
            flashTag += 'name="'+this.id+'" ';
        }
        flashTag += 'pluginspage="http://www.macromedia.com/go/getflashplayer">';
        flashTag += '</embed>';
    }
    return flashTag;
}

/**
 * Write the Flash tag out. Pass in a reference to the document to write to. 
 */
FlashTag.prototype.write = function(doc)
{
    document.write(this.toString());
}
FlashTag.prototype.debug = function(doc)
{
	document.write("<pre>" + this.toString().replace(/</gi,"&lt;").replace(/>/gi,"&gt;") + "</pre>");
}

