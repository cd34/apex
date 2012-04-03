%if form.errors.has_key('whole_form'):
	%for error in form.errors.get('whole_form'):
		<p class="field_error">${error}</p>
	%endfor
%endif

<form id="${form.__class__.__name__}" action="${action}" method="POST" accept-charset="utf-8"
	%if form.is_multipart:
		 enctype="multipart/form-data"
	%endif
	>
	<table border="0" cellspacing="0" cellpadding="2">
		%for index, field in enumerate(form):
			<tr class="${['odd', 'even'][index % 2]}">
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
	<input type="submit" name="submit" value="${submit_text}" />
</form>