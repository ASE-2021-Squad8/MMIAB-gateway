function timezoneString() {
    offset = new Date().getTimezoneOffset()
    hours = (Math.abs(offset) / 60).toString().padStart(2, "00")
    minutes = (Math.abs(offset) % 60).toString().padStart(2, "00")
    tz_string = offset < 0 ? `+${hours}:${minutes}` : `-${hours}:${minutes}`

    return tz_string
}

const b64toBlob = (b64Data, contentType = '', sliceSize = 512) => {
    const byteCharacters = atob(b64Data);
    const byteArrays = [];

    for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
        const slice = byteCharacters.slice(offset, offset + sliceSize);

        const byteNumbers = new Array(slice.length);
        for (let i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
        }

        const byteArray = new Uint8Array(byteNumbers);
        byteArrays.push(byteArray);
    }

    const blob = new Blob(byteArrays, { type: contentType });
    return blob;
}

function getAttachment(msg_id) {
    $.ajax({
        url: `/message/${msg_id}/attachment`,
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            const blob = b64toBlob(data["attachment"], "image/jpeg");
            const blobUrl = URL.createObjectURL(blob);

            window.location = blobUrl;
        },
    });
}

function buildTableReceived(data) {
    var table = document.getElementById('received');
    table.innerHTML = `<thead class="thead-light">
    <tr>
        <th class="text-center" scope="col">Sender</th>
        <th class="text-center" scope="col">E-mail</th>
        <th class="text-center" scope="col">Open message</th>
        <th class="text-center" scope="col">Reply to message</th>
        <th class="text-center" scope="col">Forward message</th>
        <th class="text-center" scope="col">Delete message for me</th>
    </tr>
</thead>`

    for (var i = 0; i < data.length; i++) {
        msg = data[i];
        user = "";
        $.ajax({
            url: '/api/user/' + msg.sender + "/public",
            type: 'GET',
            async: false,
            dataType: 'json',
            success: function (response) { user = response },
        });

        var row = `<tr>
							<td style="text-align:center">${user.firstname + " " + user.lastname}</td>
                            <td style="text-align:center">${user.email}</td>
							<td style="text-align:center"><button onclick="open_message_received(${msg.id})" class="btn btn-success">Open</button></td>
							<td style="text-align:center"><button onclick="reply_message('${user.email}', ${msg.sender})" class="btn btn-primary">Reply</button></td>
							<td style="text-align:center"><button onclick="forward_message('${user.email}','${msg.id}')" class="btn btn-primary">Forward</button></td>
							<td style="text-align:center"><button onclick="delete_message(${msg.id})" class="btn btn-danger">Delete</button></td>
							
					  </tr>`;
        table.innerHTML += row;
    }
}

function buildTableSent(data) {
    var table = document.getElementById('sent');
    table.innerHTML = `<thead class="thead-light">
    <tr class="bg-info"></tr>
    <th class="text-center">Receiver</th>
    <th class="text-center">E-mail</th>
    <th class="text-center">Open message</th>
    <th class="text-center">Forward message</th>
    </tr>
</thead>`
    for (var i = 0; i < data.length; i++) {
        msg = data[i];
        user = "";
        $.ajax({
            url: '/api/user/' + msg.recipient + "/public",
            type: 'GET',
            async: false,
            dataType: 'json',
            success: function (response) { user = response },
        });

        var row = `<tr>
								<td style="text-align:center">${user.firstname + " " + user.lastname}</td>
								<td style="text-align:center">${user.email}</tb>
								<td style="text-align:center"><button onclick="open_message_sent(${msg.id})" class="btn btn-success">Open</button></td>
								<td style="text-align:center"><button onclick="forward_message('${user.email}','${msg.id}', true)" class="btn btn-primary">Forward</button></td>
						</tr>`;
        table.innerHTML += row;
    }
}

function open_message_received(msg_id) {
    // Mark message as read
    url = '/api/message/read_message/' + msg_id;
    $.get(url);

    // Set model up to read message
    var modal = document.getElementById("modal_read");
    var modal_text = document.getElementById("modal_read_text");
    var btn = document.getElementById("myBtn");
    var span = document.getElementsByClassName("close")[0];
    modal.style.display = "block";
    modal_text.innerHTML = "<b>Loading message contents...</b>";

    // Get the message contents
    $.ajax({
        url: '/message/' + msg_id,
        type: 'GET',
        dataType: 'json',
        success: function (message) {
            var modal = document.getElementById("modal_read");
            var modal_text = document.getElementById("modal_read_text");
            var btn = document.getElementById("myBtn");
            var span = document.getElementsByClassName("close")[0];
            modal.style.display = "block";
            modal_text.innerHTML = message.text;

            if (message.has_media) {
                modal_text.innerHTML += `<a class="btn btn-secondary" href="#" onclick="getAttachment(${msg_id})">View attachment</a>`
            }
        },
        error: function () {
            var modal = document.getElementById("modal_read");
            var modal_text = document.getElementById("modal_read_text");
            modal.style.display = "block";
            modal_text.innerHTML = "<b>Something went wrong :(</b>";
        }
    })

    // Set up modal closing
    span.onclick = function () {
        modal.style.display = "none";
    }
    window.onclick = function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    }
}

function open_message_sent(msg_id) {
    // Set model up to read message
    var modal = document.getElementById("modal_read");
    var modal_text = document.getElementById("modal_read_text");
    var btn = document.getElementById("myBtn");
    var span = document.getElementsByClassName("close")[0];
    modal.style.display = "block";
    modal_text.innerHTML = "<b>Loading message contents...</b>";

    // Get the message contents
    $.ajax({
        url: '/message/' + msg_id,
        type: 'GET',
        dataType: 'json',
        success: function (message) {
            var modal = document.getElementById("modal_read");
            var modal_text = document.getElementById("modal_read_text");
            var btn = document.getElementById("myBtn");
            var span = document.getElementsByClassName("close")[0];
            modal.style.display = "block";
            modal_text.innerHTML = message.text;

            if (message.has_media) {
                modal_text.innerHTML += `<a class="btn btn-secondary" href="#" onclick="getAttachment(${msg_id})">View attachment</a>`
            }
        },
        error: function () {
            var modal = document.getElementById("modal_read");
            var modal_text = document.getElementById("modal_read_text");
            var btn = document.getElementById("myBtn");
            var span = document.getElementsByClassName("close")[0];
            modal.style.display = "block";
            modal_text.innerHTML = "<b>Something went wrong :(</b>";
        }
    })

    // Set up modal close
    span.onclick = function () {
        modal.style.display = "none";
    }
    window.onclick = function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    }
}

function reply_message(msg_email, recipient_id) {
    var modal_reply = document.getElementById("modal_reply");
    var spanReply = document.getElementsByClassName("close")[1];
    var modal_reply_content = document.getElementById("recipient_reply");

    console.log(msg_email + " " + recipient_id)

    modal_reply_content.textContent = msg_email;
    modal_reply_content.value = recipient_id;

    $('#recipient').empty()
    get_recipient();
    modal_reply.style.display = "block";

    //Close modal
    spanReply.onclick = function () {
        modal_reply.style.display = "none";
    }

    //Close modal
    window.onclick = function (event) {
        if (event.target === modal_reply) {
            modal_reply.style.display = "none";
        }
    }

}

function forward_message(msg_email, msg_id, forwarding_sent = false) {
    var modal_forward = document.getElementById("modal_forward");
    var spanForward = document.getElementsByClassName("close")[2];
    CKEDITOR.instances.fwd_text.setData("<b>Loading message contents...</b>");

    $('#recipient').empty()
    get_recipient();
    modal_forward.style.display = "block";

    // Get the message contents
    $.ajax({
        url: '/message/' + msg_id,
        type: 'GET',
        dataType: 'json',
        success: function (message) {
            msg_data = "<p>Message forwarded from " + msg_email + ":</p>";
            msg_data += message.text;
            CKEDITOR.instances.fwd_text.setData(msg_data);
        },
        error: function () {
            var modal = document.getElementById("modal_read");
            var modal_text = document.getElementById("modal_forward");
            modal.style.display = "block";
            modal_text.innerHTML = "<b>Something went wrong :(</b>";
        }
    })

    // Setup modal closing
    spanForward.onclick = function () {
        modal_forward.style.display = "none";
    }
    window.onclick = function (event) {
        if (event.target === modal_forward) {
            modal_forward.style.display = "none";
        }
    }
}

function delete_message(msg_id) {
    $.ajax({
        url: '/api/message/' + msg_id,
        type: 'DELETE',
        success: function () {
            alert("Message deleted");
            location.reload(true);
        },
    });
}

function get_recipient() {
    $.ajax({
        url: "/api/user/recipients",
        contentType: "application/json",
        dataType: "json",
        success: function (data, status) {
            console.log("status " + status);
            items = data;
            $.each(items, function (i, item) {
                $('#recipient').append($('<option>', {
                    value: item.id,
                    text: item.email
                }));
            });
            loaded = true;
        },
        error: function (a, b, c) {
            console.log(a + " " + b + " " + c)
        }
    });
}

function send_msg_reply_forward(form_id, forwarding = false) {
    let inputform = $('#' + form_id)
    let request_data = new FormData(inputform[0]);

    if (forwarding) {
        request_data.set("text", CKEDITOR.instances.fwd_text.getData())
    } else {
        request_data.set("text", CKEDITOR.instances.reply_text.getData())
    }

    if ($.trim(request_data.get("text")).length === 0) {
        return alert("Text cannot be empty");
    }

    var inputDate = new Date(request_data.get("delivery_date"));
    var now = new Date();
    if (inputDate < now) {
        return alert("Date cannot be in the past")
    }

    request_data.set("timezone", timezoneString());

    $.ajax({
        url: "/message",
        data: request_data,
        contentType: false,
        processData: false,
        type: "POST",
        success: function () {
            alert("Message successfully sent");
        },
        error: function (a, b, c) {
            console.log(a + " " + b + " " + c);
            alert("Oops, something went wrong");
        }
    });
}
