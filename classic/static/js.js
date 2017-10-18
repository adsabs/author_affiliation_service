/**
 * Javascript for  Author-Affiliation Form
 */

//function that deselect all the author's affiliations if I remove the author
function check_aff(obj)
{
	//if I'm deselecting the current checkbox, I have to deselect also the connected affiliations
	if (! $(obj).attr('checked'))
	{
		//I get the id
		var curid = $(obj).attr('id');
		//I set a counter
		var i = 1;
		while ($('#'+curid+'_affiliation_'+i).length > 0)
		{
			$('#'+curid+'_affiliation_'+i).removeAttr("checked");
			i++;
		}
	}
};


//function that select the author if I select at least one affiliation
function check_auth(obj)
{
	//If I select a checkbox of the affiliation, I have to select also its author
	if ($(obj).attr('checked'))
	{
		//I get the id
		var curid = $(obj).attr('id');
		//I extract the author id
		var curidlist = curid.split('_');
		var authorid = curidlist[0]+'_'+curidlist[1];
		//I check the checkbox
		$('#'+authorid).attr("checked","checked");
	}
};

//function that syncs the two selects at the top and bottom of the form
function syncronize_select(obj)
{
	if($(obj).attr('id') == 'select_top')
	{
		//I get the current value
		var value = $('#select_top > option:selected').val();
		//I set the other select
		$('#select_bottom > option[value='+value+']').attr('selected', 'selected');
	}
	else if($(obj).attr('id') == 'select_bottom')
	{
		//I get the current value
		var value = $('#select_bottom > option:selected').val();
		//I set the other select
		$('#select_top > option[value='+value+']').attr('selected', 'selected');
	}
};