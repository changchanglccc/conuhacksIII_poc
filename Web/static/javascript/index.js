document.body.onload = loadFrames;

function loadClassifier(id, parent) {
    // addElement ();

    var client = new sendRequest();
    client.get('http://ec2-18-217-218-155.us-east-2.compute.amazonaws.com/rest/api/detector', function(response) {
        var detData = JSON.parse(response).classifieres;
        var cont1 = document.createElement("div");
        cont1.className = "dropdown"
        parent.appendChild(cont1)
        var button1 = document.createElement("button");
        button1.className = "btn btn-secondary dropdown-toggle"
        button1.setAttribute('type', 'button')
        button1.setAttribute('id','dropdownMenuButton')
        button1.setAttribute('data-toggle', 'dropdown')
        button1.setAttribute('aria-haspopup', 'true')
        button1.setAttribute('aria-expanded', 'false')
        button1.appendChild(document.createTextNode("ClassifierList"))
        cont1.appendChild(button1)
        var cont2 = document.createElement("div");
        cont2.className = "dropdown-menu"
        cont2.setAttribute('aria-labelledby', 'dropdownMenuButton')
        cont1.appendChild(cont2)
        for (index in detData){
            de = detData[index];
            expandMenu(id, de, cont2)
        }
    });
}

function loadFrames() {
    // addElement ();
    var client = new sendRequest();
    client.get('http://ec2-18-217-218-155.us-east-2.compute.amazonaws.com/rest/api/camera', function(response) {
        var camera = JSON.parse(response);
        for (index in camera){
            cameraid = camera[index];
            addElement (cameraid);
        }
    });
}

function addElement (cameraid) {
    // create a new div element
    var newDiv = document.createElement("div");
    newDiv.className = 'col-sm-6 col-md-4'
    var div2 = document.createElement("div");
    div2.className = "frame-wrapper"
    newDiv.appendChild(div2)
    var div3 = document.createElement("div");
    div3.className = "frame-title"
    div3.appendChild(document.createTextNode(cameraid.camera_id))
    div2.appendChild(div3)
    var div4 = document.createElement("div");
    div4.className = "frame-stage"
    div2.appendChild(div4)
    var div5 = document.createElement("div");
    div5.className = "embed-responsive embed-responsive-16by9"
    div4.appendChild(div5)
    var iframe1 = document.createElement("img");
    iframe1.className = "embed-responsive-item"
    // iframe1.src = "static/some.jpg"
    refreshFrame(iframe1, cameraid.camera_id, div2)
    div5.appendChild(iframe1)
    var div6 = document.createElement("div");
    div6.className = "switch-toggle"
    div2.appendChild(div6)
    var div7 = document.createElement("div");
    div7.className = "frame-notes"
    div7.appendChild(document.createTextNode(cameraid.classifier_name))
    div2.appendChild(div7)

    loadClassifier(cameraid.camera_id, div7)

    // add the newly created element and its content into the DOM
    var currentDiv = document.getElementById("cameras");
    currentDiv.appendChild(newDiv)
}

function expandMenu(id, de, cont2){
    //dropdown menu

    var but_func = document.createElement("button");
    but_func.className = "dropdown-item"
    but_func.setAttribute('type', 'button')
    but_func.setAttribute('onclick', function(){
        setCamera(id, de.name);
    });
    but_func.addEventListener("click", function(){
        setCamera(id, de.name);
    });
    but_func.setAttribute('return', 'false')
    text = document.createTextNode(de.name)
    but_func.appendChild(document.createTextNode(de.name))
    cont2.appendChild(but_func)
}

function setCamera(id, name) {
    var client = new sendRequest();
    var params = "camera_id="+id + "&classifier_name=" +name
    client.post('http://ec2-18-217-218-155.us-east-2.compute.amazonaws.com/rest/api/camera/setting', function(response) {

    }, params);
}

var sendRequest = function() {
    this.get = function(path, callback) {
        var requestClient = new XMLHttpRequest();
        requestClient.onreadystatechange = function() {
            if (requestClient.readyState == 4 && requestClient.status == 200)
                callback(requestClient.responseText);
        }

        requestClient.open( "GET", path, true );
        requestClient.send( null );
    }

    this.post = function (path, callback, params) {
        var requestClient = new XMLHttpRequest();
        requestClient.open("POST", path, true);

        //Send the proper header information along with the request
        requestClient.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

        requestClient.onreadystatechange = function() {//Call a function when the state changes.
            if(requestClient.readyState == 4 && requestClient.status == 200) {
                callback(requestClient.responseText);
            }
        }
        requestClient.send(params);
    }
}

function setAlarmNotification(div2) {
    div2.style.borderColor = "red";
    div2.style.borderWidth = "5px";
}

function refreshFrame(src, id, div2) {

    var client = new sendRequest();
    var params = "camera_id="+id
    client.post('http://ec2-18-217-218-155.us-east-2.compute.amazonaws.com/rest/api/check', function(response) {
        if(!response.includes("Error")) {
            if(response.includes("alert")) {
                //set alert
                setAlarmNotification(div2)
            } else {
                div2.style.borderColor = "#2f4f4f";
                div2.style.borderWidth = "1px";
            }
            src.src = response;
        }
    }, params);

    setTimeout(function() {
        refreshFrame(src, id, div2);
    }, 1000)

}