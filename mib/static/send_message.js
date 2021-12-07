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

$(document).ready(function () {
    get_recipient();
    $.ajax({
        url: '/message/draft',
        type: 'GET',
        dataType: 'json',
        success: buildTable
    })
});

function buildTable(data) {
    var table = document.getElementById('draftsTable')

    if (data.length == 0) {
        table.innerHTML = "No drafts!"
        return
    }

    table.innerHTML = `<thead class="thead-light">
        <tr class="bg-info">
        <th scope="col">Recipient</th>
        <th scope="col">E-mail</th>
        <th scope="col">Text</th>
        <th scope="col">Actions</th>
    </tr>
    </thead>`

    for (var i = 0; i < data.length; i++) {
        msg = ""
        $.ajax({
            url: '/api/message/draft/' + data[i].id,
            type: 'GET',
            async: false,
            dataType: 'json',
            success: function (response) { msg = response }
        })

        if (data[i].has_media) {
            msg.text += `<a class="btn btn-secondary" href="#" onclick="getAttachment(${data[i].id})">View attachment</a>`
        }

        var row = `<tr>`

        if (msg.recipient) {
            user = ""
            $.ajax({
                url: '/api/user/' + msg.recipient + "/public",
                type: 'GET',
                async: false,
                dataType: 'json',
                success: function (response) { user = response },
            })
            
            row += `<td>${user.firstname + " " + user.lastname}</td><td>${user.email}</td>`
        } else {
            row += `<td>None</td><td>None</td>`
        }

        row += `<td>${msg.text}</td>
                <td>`

        if (data[i].has_media) {
            row += `<input id="removeattachment" type="button" class="btn btn-outline-primary" value="Purge attachment" onclick="removeAttachment(${data[i].id})"/> `
        }

        row += `<input id="editdraft" type="button" value="Edit" class="btn btn-primary" onclick="editDraft(${data[i].id})" />
                <input id="deldraft" type="button" class="btn btn-danger" value="Delete" onclick="deleteDraft(${data[i].id})" />
                </td></tr>`

        table.innerHTML += row
    }
}

function deleteDraft(draft_id) {
    $.ajax({
        url: '/api/message/draft/' + draft_id,
        type: 'DELETE',
        success: function () {
            alert("Draft deleted")
            location.reload(true)
        },
    })
}

function removeAttachment(draft_id) {
    $.ajax({
        url: '/api/message/draft/' + draft_id + '/attachment',
        type: 'DELETE',
        success: function () {
            location.reload(true)
        },
    })
}

function editDraft(draft_id) {
    $.ajax({
        url: '/api/message/draft/' + draft_id,
        type: 'GET',
        dataType: 'json',
        success: function (response) {
            var recipient = document.getElementById('recipient')
            var draft_hidden_field = document.getElementById('draft_id')

            CKEDITOR.instances.text.setData(response.text);
            recipient.value = response.recipient
            draft_hidden_field.value = draft_id
        }
    })
}