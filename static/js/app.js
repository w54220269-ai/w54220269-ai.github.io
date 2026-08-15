function submitPairing() {
    var pin = document.getElementById('pinInput').value;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/pair", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                alert("تم الاقتران بنجاح!");
                document.getElementById('pairSection').style.display = 'none';
                document.getElementById('appsSection').style.display = 'block';
                window.currentPin = pin;
                loadApps();
            } else {
                alert("رمز اقتران غير صحيح!");
            }
        }
    };
    xhr.send(JSON.stringify({ pin: pin }));
}

function loadApps() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/api/apps", true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var res = JSON.parse(xhr.responseText);
            var list = document.getElementById('appsList');
            list.innerHTML = '';
            for (var i = 0; i < res.packages.length; i++) {
                var pkg = res.packages[i];
                var li = document.createElement('li');
                li.innerHTML = pkg + ' <button class="btn" onclick="sendApp(\'' + pkg + '\')">نقل</button>';
                list.appendChild(li);
            }
        }
    };
    xhr.send();
}

function sendApp(pkg) {
    alert("بدأ استخراج ونقل: " + pkg);
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/transfer", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(JSON.stringify({ pin: window.currentPin, package_name: pkg }));
}

function checkStatus(pin) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/api/status/" + pin, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var data = JSON.parse(xhr.responseText);
            document.getElementById('statusText').innerText = data.status;
            document.getElementById('progressBar').style.width = data.progress + '%';
            if (data.file_ready) {
                document.getElementById('fileInfo').innerHTML = 
                    '<p>الملف جاهز: ' + data.file_ready + '</p>' +
                    '<a href="/download/' + data.file_ready + '"><button class="btn">تحميل الملف على التلفاز</button></a>';
            }
        }
    };
    xhr.send();
}
