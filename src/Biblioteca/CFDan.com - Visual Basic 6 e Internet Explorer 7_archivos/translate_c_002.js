function setAS() {
	try {
		document.blogPostCommentForm.sfc.value = "OK";
	}catch(e){
	
	}
	try {
		if( $("sfc") ) { 
			$("sfc").value = "OK";
		}
	} catch(e){}
}

function toggle(id)
{
	$(id).style.display = $(id).style.display=='none'?"block":"none";
}

function openWin( loc, width, height, bResize, sHandle, bLockOpen, bScrollbars )
{
	if( arguments.length < 1 ) return;
	if( arguments.length < 2 ) width = 800;
	if( arguments.length < 3 ) height = 600;
	if( arguments.length < 4 ) bResize = false;
	if( arguments.length < 5 ) sHandle = false;
	if( arguments.length < 6 ) bLockOpen = false;
	if( arguments.length < 7 ) bScrollbars = false;

	var sLeft=(screen.width-width)/2, sTop=(screen.height-height)/2;
	var params = "height=" + height + ", width=" + width + ", top=" + sTop + ", left=" + sLeft + ", scrollbars=" + (bScrollbars?"yes":"no")+ ", resizable=" + (bResize?"yes":"no");
	window.open( loc, sHandle, params );
}

var cftopper = {};

function reportError(request)
{
	alert('Sorry. There was an error.');
}

cftopper.getLoadingHTML = function()
{
	return '<div style="padding:10px;"><img src="images/loading-circ.gif" width="18" height="18" alt="" border="0" align="absmiddle" hspace="4"/><strong style="color:#BBB;">Loading...</strong></div>';
}

cftopper.showAddCommentForm = function(blogPostId)
{
	$('blogPostCommentFormHolder'+blogPostId).innerHTML = cftopper.getLoadingHTML();
	$('blogPostCommentFormHolder'+blogPostId).style.display = "block";
	var url = "index.cfm?action=getBlogPostCommentForm"+ "&"+(new Date()).getTime();
	var pars = 'blogPostId='+blogPostId;
	var myAjax = new Ajax.Updater(
		'blogPostCommentFormHolder'+blogPostId, 
		url, 
		{
			method: 'post', 
			parameters: pars,
			onFailure: reportError
		});
}

cftopper.getComments = function(blogPostId)
{
	$('blogpostcomments'+blogPostId).innerHTML = cftopper.getLoadingHTML();
	$('blogpostcomments'+blogPostId).style.display = "block";
	var url = "index.cfm?action=getBlogPostComments";
	var pars = 'blogPostId='+blogPostId;
	var myAjax = new Ajax.Updater(
		'blogpostcomments'+blogPostId, 
		url, 
		{
			method: 'post', 
			parameters: pars,
			onFailure: reportError
		});
}

cftopper.formErrorCheck = function( thId, isOK )
{
	$(thId).className = isOK?"":"thError";
	return isOK;
}

cftopper.postComment = function(blogPostId)
{
	var cSubscribe="No";
	
	if(document.getElementById("rb1").checked) {
		cSubscribe = "Yes";
	}
	
	with( $("blogPostCommentForm"+blogPostId) )
	{
		var bFormIsOK = true;
		bFormIsOK &= cftopper.formErrorCheck( 'bp_th_name'+blogPostId, ( name.value.length > 2 )  );
		bFormIsOK &= cftopper.formErrorCheck( 'bp_th_email'+blogPostId, ( email.value.length > 2 )  );
		bFormIsOK &= cftopper.formErrorCheck( 'bp_th_country'+blogPostId, ( countrycode.selectedIndex > 0 )  );
		bFormIsOK &= cftopper.formErrorCheck( 'bp_th_comment'+blogPostId, ( comment.value.length > 0 && comment.value != 'Type your comment here' )  );
		bFormIsOK &= cftopper.formErrorCheck( 'bp_th_mySum'+blogPostId, ( mySum.value != "0" )  );
		
		if( !bFormIsOK ) return;
				
		//Send the comment
		var dataURL = "index.cfm?action=postBlogComment&blogPostId=" + blogPostId;
		pars = 'name=' + name.value;
		pars += '&email=' + email.value;
		pars += '&subscribe=' + cSubscribe;
		pars += '&sfc=' + sfc.value;
		pars += '&mySum=' + mySum.value;
		pars += '&countrycode=' + countrycode.options[countrycode.selectedIndex].value;
		if( userURL.value.length ) pars += '&userURL=' + userURL.value;
		pars += '&comment=' + comment.value;
		
		var myAjax = new Ajax.Request(
				dataURL, 
				{
					method: 'post', 
					parameters: pars, 
					onComplete: function(req){cftopper.getComments(blogPostId)}
				});
				
		if( name.value != "Topper" )
		$("blogPostCommentFormHolder"+blogPostId).style.display = "none";
	}
}