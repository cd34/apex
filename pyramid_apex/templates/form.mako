<style type="text/css" media="screen">
.field_error {
	color: #f00;
}
.required_star {
	color: #f00;
	font-size: 10pt;
}
.help_text {
	font-size: 10pt;
}
td {
  vertical-align: top;
}
#field_error_back {
	background: #fcc;
}
</style>

%if form.errors.has_key('whole_form'):
	%for error in form.errors.get('whole_form'):
		<p class="field_error">${error}</p>
	%endfor
%endif

<table border="0" cellspacing="0" cellpadding="2">
	%for field in form:
		<tr class="{{ loop.cycle('odd', 'even') }}">
			<td class="label_col">${field.label} 
			%if field.flags.required:
				<span class="required_star">*</span>
			%endif
			</td>
			<td class="field_col">${field}
				%if field.description:
					<span class="help_text">${field.description}</span>
				%endif
				%for error in field.errors:
					<span class="field_error">${error}</span>
				%endfor
			</td>
		</tr>
	%endfor
	${csrf_token_field|n}
</table>