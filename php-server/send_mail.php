<!DOCTYPE html>
<html>
<body>

<title> Termostatino prototipo </title>
<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
	echo "<p> I will send a mail with info on temp</p>";
	echo "<p>";
	echo $_POST["temp"];
	echo "</p>";
}
?>

https://github.com/PHPMailer/PHPMailer

</body>
