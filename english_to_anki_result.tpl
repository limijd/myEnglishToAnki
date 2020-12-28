<html>
<body>

<h3>
Congratulations!
</h3>

<table>
    <tr>
        <td>Total ANKI cards created</td>
        <td>{{len(eta.anki_cards)}}</td>
    </tr>
    <tr>
        <td>Total TTS mp3 audio generated</td>
        <td>{{eta.generated_mp3}}</td>
    </tr>
    <tr>
        <td>compressed tarball(.gz) created</td>
        <td>{{request.anki_import_filename}}</td>
    </tr>
    <tr>
        <td>compressed tarball size</td>
        <td>{{eta.tarball_size}} bytes</td>
    </tr>

</table>

<h3>Download link:</h3>
<a href="{{request.APPROOT}}/web_download/{{request.anki_import_filename}}">{{request.anki_import_filename}}</a>

<h3>注意! 如果你是第一次导入本页面生成的ANKI笔记, 请先导入以下ANKI记忆库模版, 这样对应的笔记类型才会随记忆库自动导入ANKI系统。</h3>
<br>
<a href="{{request.APPROOT}}/web_download/myEnglishV202012.apkg">下载记忆库模版</a>
</body>
</html>
