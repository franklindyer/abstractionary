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

function state_update_loop(sock) {
    var state = {
        "player_id": get_cookie("player_id"),
        "player_name": get_cookie("name"),
        "desc_field": document.getElementById("player-input").value,
    };
    var state_string = JSON.stringify(state);
    sock.emit('gamemsg', { data: state_string });
    setTimeout(() => { state_update_loop(sock); }, 500);
};

// Credit to Dan Abramov for this custom hook
// https://overreacted.io/making-setinterval-declarative-with-react-hooks/
function useInterval(callback, delay) {
  const savedCallback = React.useRef();
 
  // Remember the latest callback.
  React.useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);
 
  // Set up the interval.
  React.useEffect(() => {
    function tick() {
      savedCallback.current();
    }
    if (delay !== null) {
      let id = setInterval(tick, delay);
      return () => clearInterval(id);
    }
  }, [delay]);
}

function HintInput({enabled, onChange}) {
    const handleChange = (event) => {
        onChange(event.target.value);
    };
    return (
        <textarea 
            maxLength="10000" 
            className="player-hint-box" 
            id="player-input" 
            onChange={handleChange}
            defaultValue="A monad is just a monoid in the category of endofunctors."> 
        </textarea>
    );
};

function HintOutput({ outputHint }) {
    console.log(outputHint);
    return (
        <textarea
            className="player-hint-box"
            id="player-output"
            value={outputHint}
            disabled>
        </textarea>
    )
}

var socket = io();
var ticker = new EventTarget();
const tickEvent = new Event("tick");
setInterval(() => { ticker.dispatchEvent(tickEvent) }, 2000);

function App() {
    const defaultString = "A monad is just a monoid in the category of endofunctors."

    const [hintInString, setHintInString] = React.useState(defaultString);
    const [hintOutString, setHintOutString] = React.useState("");
    const [chatMessages, setChatMessages] = React.useState([]);

    const [gameData, setGameData] = React.useState({});

    const sendState = () => {
        var state = {
            "player_id": get_cookie("player_id"),
            "player_name": get_cookie("name"),
            "desc_field": hintInString,
        }
        var state_string = JSON.stringify(state);
        socket.emit('gamemsg', { data: state_string });
    }

    const onUpdate = (data) => {
        var data_dict = JSON.parse(data);
        setHintOutString(data_dict["desc_field"]);
        setChatMessages(data_dict["chat"]);
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
            <HintInput enabled={true} onChange={setHintInString} />
            <HintOutput outputHint={hintOutString} />
            <img src='/static/icon_1.png'></img>
        </div>
    );
};

var body = ReactDOM.createRoot(document.getElementById("play-game-div"));
body.render(<App />)
