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
	%for loop, field in enumerate(form):
		<fieldset>
			<legend>${field.label}
				%if field.flags.required:
					<span class="required_star">*</span>
				%endif
			</legend>
			${field}
			%for error in field.errors:
				<span class="field_error">${error}</span>
			%endfor
			%if field.description:
				<br />
				<span class="help_text">${field.description}</span>
			%endif
		</fieldset>
	%endfor
	${csrf_token_field|n}
	<input type="submit" name="submit" value="${submit_text}" />
</form>