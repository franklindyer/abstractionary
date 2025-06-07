const get_cookie = (name) => {
    return document.cookie.split('; ').reduce((r, v) => {
        const parts = v.split('=')
        return parts[0] === name ? decodeURIComponent(parts[1]) : r
    }, '')
}

if (get_cookie("name") === "") {
    document.cookie = `name=${window.prompt("What is your nickname?")}`;
}

var socket = io(); 

function HintInput({enabled, onChange}) {
    const handleChange = (event) => {
        onChange(event.target.value);
    };
    const onHintKeydown = (e) => {
        if (e.keyCode === 13) {
            e.preventDefault();
            socket.emit('chat', { data: JSON.stringify({
                player_id: get_cookie("player_id"),
                chat_msg: e.target.value
            }) });
            e.target.value = "";
            onChange("");
        }
    }
    return (
        <textarea 
            maxLength="10000" 
            className="player-hint-box" 
            id="player-input" 
            onChange={handleChange}
            onKeyDown={onHintKeydown}
            defaultValue="A monad is just a monoid in the category of endofunctors."
            disabled={!enabled}> 
        </textarea>
    );
};

function HintOutput({ outputHint }) {
    return (
        <textarea
            className="player-hint-box"
            id="player-output"
            value={outputHint}
            disabled>
        </textarea>
    )
}

function PlayerThumbnail({ player }) {
    return (
        <div className="player-thumbnail">
            <img src={player["icon"]} className="player-icon"></img>
            <b className='player-nametag'>{player["name"]}<br></br>{player["points"]} points</b>
        </div>
    )
}

function PlayerScoreboard({ playerList }) {
    const thumbnails = playerList.map((person) =>
        <PlayerThumbnail player={person} />
    );
    return (
        <div id="players-box">
            {thumbnails}
        </div>
    );
}

function ChatMessage({ chatMsg }) {
    if (chatMsg[0] == "WIN")
        return (
            <a className="chat-message win-chat-message">{chatMsg[2]}</a>
        );
    else if (chatMsg[0] == "HINT")
        return (
            <a className="chat-message highlighted-chat-message">
                <b>{chatMsg[1]}</b>
                <a>: {chatMsg[2]}</a>
            </a>
        );
    else
        return (
            <a className="chat-message">
                <b>{chatMsg[1]}</b>
                <a>: {chatMsg[2]}</a>
            </a>
        )
}

function ChatHistory({ enabled, chatList }) {
    const chatBoxes = chatList.map((chat) => 
        <ChatMessage chatMsg={chat} />
    );
    const onChatKeydown = (e) => {
        if (e.keyCode === 13) {
            socket.emit('chat', { data: JSON.stringify({
                player_id: get_cookie("player_id"),
                chat_msg: e.target.value
            }) });
            e.target.value = "";
        }
    }
    return (
        <div id="player-chat">
            <input 
                type="text" 
                id="chat-input" 
                spellCheck="true" 
                onKeyDown={onChatKeydown}
                disabled={!enabled}>
            </input>
            {chatBoxes}
        </div>
    );
}

function TargetWordChoice({ targetWord, chooseTargetWord }) {
    var chooseTarget = (e) => {
        chooseTargetWord(targetWord);
    };
    return (
        <b class="target-word-b target-word-choice" value="{ targetWord }" onClick={ chooseTarget }>
            { targetWord }
        </b>
    )
}

function LevelHeader({ isIlliterate, targetWords, targetWord, describer, chooseTargetWord }) {
    if (!isIlliterate)
        return (
            <div id="player-help">
                {describer} is The Illiterate. Try and guess the word they are describing.
            </div>
        )
    else if (targetWord.length > 0)
        return (
            <div id="player-help">
                You are The Illiterate. Make the other player guess the phrase: <b class="target-word-b">{targetWord}</b>
            </div>
        )
    else
        return (
            <div id="player-help">
                It's your turn to be The Illiterate! Pick one of these phrases: {targetWords.map((tw) => {
                    return <TargetWordChoice targetWord={tw} chooseTargetWord={chooseTargetWord} />;
                })}
            </div>
        )
}

var socket = io();
var ticker = new EventTarget();
const tickEvent = new Event("tick");
setInterval(() => { ticker.dispatchEvent(tickEvent) }, 1000);

function App() {
    const defaultString = "A monad is just a monoid in the category of endofunctors."

    const [hintInString, setHintInString] = React.useState(defaultString);
    const [hintOutString, setHintOutString] = React.useState("");
    const [chatInString, setChatInString] = React.useState("");
    const [playerList, setPlayerList] = React.useState([]);
    const [chatMessages, setChatMessages] = React.useState([]);
    const [isCurrentPlayer, setIsCurrentPlayer] = React.useState(false);
    const [targetWords, setTargetWords] = React.useState([]);
    const [targetWord, setTargetWord] = React.useState("");
    const [describer, setDescriber] = React.useState("");

    const [gameData, setGameData] = React.useState({});

    const sendState = () => {
        var state = {
            "player_id": get_cookie("player_id"),
            "player_name": get_cookie("name"),
            "desc_field": hintInString,
            "target_word": targetWord
        }
        var state_string = JSON.stringify(state);
        socket.emit('gamemsg', { data: state_string });
    }

    const onUpdate = (data) => {
        var data_dict = JSON.parse(data);
        setHintOutString(data_dict["desc_field"]);
        setPlayerList(data_dict["players"]);
        setChatMessages(data_dict["chat"]);
        setDescriber(data_dict["describer"]);
        if ("target_words" in data_dict) {
            setTargetWords(data_dict["target_words"]);
            setIsCurrentPlayer(true);
        } else {
            setTargetWords([]);
            setTargetWord("");
            setIsCurrentPlayer(false);
        }
    }

    React.useEffect(() => {
        socket.on('gamemsg', onUpdate);
        return () => { socket.off('gamemsg', onUpdate); }
    }, []);

    React.useEffect(() => {
        ticker.addEventListener("tick", sendState);
        return () => ticker.removeEventListener("tick", sendState);
    });

    return (
        <div>
            <LevelHeader isIlliterate={isCurrentPlayer} targetWords={targetWords} targetWord={targetWord} describer={describer} chooseTargetWord={setTargetWord} />
            <HintInput enabled={isCurrentPlayer && targetWord.length > 0} onChange={setHintInString} />
            <HintOutput outputHint={hintOutString} />
            <div id="chat-section-container">
                <PlayerScoreboard playerList={playerList} />
                <ChatHistory enabled={!isCurrentPlayer} chatList={chatMessages} />
            </div>
        </div>
    );
};

var body = ReactDOM.createRoot(document.getElementById("play-game-div"));
body.render(<App />)
