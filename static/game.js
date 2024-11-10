player_input = document.getElementById("player-input");
player_output = document.getElementById("player-output");
chat_input = document.getElementById("chat-input");
chat_output = document.getElementById("player-chat")
player_hint = document.getElementById("active-player-hint");
players_box = document.getElementById("players-box");

const get_cookie = (name) => {
    return document.cookie.split('; ').reduce((r, v) => {
        const parts = v.split('=')
        return parts[0] === name ? decodeURIComponent(parts[1]) : r
    }, '')
}

if (get_cookie("name") === "") {
    document.cookie = `name=${window.prompt("What is your nickname?")}`;
}

function state_update_loop(sock) {
    var state = {
        "player_id": get_cookie("player_id"),
        "player_name": get_cookie("name"),
        "desc_field": document.getElementById("player-input").value,
    };
    var state_string = JSON.stringify(state);
    sock.emit('gamemsg', { data: state_string });
    setTimeout(() => { state_update_loop(sock); }, 500);
}

var socket = io(); 
socket.on('connect', () => {
    state_update_loop(socket);
});
socket.on('gamemsg', (data) => {
    var data_dict = JSON.parse(data);
    
    player_output.textContent = data_dict["desc_field"];
    player_output.scrollTop = player_output.scrollHeight;
    chat_output.innerHTML = "";
    for (var cur of data_dict["chat"]) {
        var p = document.createElement('a');
        p.style.display = "block";
        if (cur[0] == "WIN") {
            p.textContent = cur[2];
            p.style.color = "green";
        } else {
            b = document.createElement('b');
            b.textContent = cur[1];
            a = document.createElement('a');
            a.textContent = `: ${cur[2]}`;
            p.appendChild(b); p.appendChild(a);
            p.classList.add("chat-message");
            if (cur[0] == "HINT") {
                p.classList.add("highlighted-chat-message");
            }
//                p. = `${cur[1]} guessed "${cur[2]}"`;
        }
        chat_output.appendChild(p);
    }

    for (var p of data_dict["players"]) {
        var player_thumb = document.getElementById(`player-thumbnail-${p["id"]}`)
        if (player_thumb === null) {
            player_thumb = document.createElement('div');
            player_thumb.classList.add('player-thumbnail');
            player_thumb.id = `player-thumbnail-${p["id"]}`;
            player_icon = document.createElement('img');
            player_icon.classList.add('player-icon')
            player_icon.src = p["icon"];
            player_name = document.createElement('b');
            player_name.classList.add("player-nametag");
            player_name.id = `player-nametag-${p["id"]}`;
            player_name.textContent = `${p["name"]}\n${p["points"]} points`
            player_thumb.appendChild(player_icon);
            player_thumb.appendChild(player_name);
            players_box.appendChild(player_thumb);
        } else {
            nametag = document.getElementById(`player-nametag-${p["id"]}`);
            nametag.innerText = `${p["name"]}\n${p["points"]} points`;
        }
    }

    if ("target_word" in data_dict) {
        player_hint.innerHTML 
            = `It's your turn to be The Illiterate! Your word is: <b>${data_dict["target_word"]}</b>`;
        if (player_input.disabled)
            player_input.value = `my word is "${data_dict['target_word']}"`;
        player_input.disabled = false;
        chat_input.disabled = true; 
    } else {
        player_hint.innerHTML = `${data_dict["describer"]} is The Illiterate. Try and guess the word they are describing.`;
        player_input.value = "";
        player_input.disabled = true;
        chat_input.disabled = false; 
    }
});
chat_input.onkeydown = (e) => {
    if (e.keyCode === 13) {
        socket.emit('chat', { data: JSON.stringify({ 
                player_id: get_cookie("player_id"),
                chat_msg: chat_input.value,
            })
        });
        chat_input.value = "";
    }
};
player_input.onkeyup = (e) => {
    if (e.keyCode === 13) {
        socket.emit('chat', { data: JSON.stringify({ 
                player_id: get_cookie("player_id"),
                chat_msg: player_input.value,
            })
        });
        player_input.value = "";
        return false;
    }
};
