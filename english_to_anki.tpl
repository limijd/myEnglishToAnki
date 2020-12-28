<form 
    id="form_EnglishToAnki" 
    name="from_EnglishtToAnki" 
    role="form" 
    action="{{request.APPROOT}}/english_to_anki_post" 
    method=post
>

<textarea rows=20 cols=50 name="inpEnglishContent" id="inpEnglishContent"></textarea>
<br>
<br>
<button type="submit">Submit</button>

</form>
