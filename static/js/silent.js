$( document ).ready(function(){
	$("a.quiet").live("click", function(){
		var self = this;
		$(this).load( $(this).attr("href"), function( data ){
			$(self).html(data);
		} );
		return false;
	});
	$("form.enter").live("keypress", function( event ){
		if( event.which == 13 ){
			
			$(this).submit();
			$( 'textarea').clear();
		}
			
	});
	$("a.see_comments").live("click", function(){
		$(".comments").each( function(){
			$(this).parent().html('<a class="replacement see_comments" href="/comment/'+$(this).find(".comid").html()+' " >See comments </a>')
		});
		return false;
	});
	$("form.comment").live("submit", function(){
		
		var parent = $(this).parent();
		request = new FormData();
		request.append( 'csrfmiddlewaretoken' ,$('form input[name="csrfmiddlewaretoken"]').val() );
		request.append( 'content' , $('form input[name="content"]').val() );
		request.append( 'text' , $('form textarea[name="text"]').val() );
		$.ajax({
	        url: $(this).attr("action"),
	        data: request,
	        processData: false,
	        contentType: false,
	        type: 'POST',
	        success: function ( data ) {
	        	if( data != "0" ){
	        		parent.html( data );
	        	}
	        	
	        }
	    });

	   
		
		
		return false
		
	});
	$("form.comment").live("keypress", function( event ){
		if( event.which == 13 ){
			$(this).submit();
		}
		
	});
	
	$("a.replacement").live("click", function(){
		var parent = $(this).parent();
		$.get( $(this).attr("href") , function( data ){
			parent.html( data );
		});
		return false;
	});

	$("a.loader").each(function(){
		var parent = $(this).parent();
		$.get( $(this).attr("href"), function( data ){
			parent.html( data );
		} );
	});
	function replace(){
		$("a.joiner").each(function(){
			var self = $(this);
			$.get( $(this).attr("href"), function( data ){
				self.replaceWith( data );
			} );
		});
	}
	replace();
	setInterval( function(){
		replace();
	},10000);
	
});