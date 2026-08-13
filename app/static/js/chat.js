let conversationId = sessionStorage.getItem("conversation_id");
let isStreaming = false;

const chatList = document.getElementById("chat-list");

const messagesContainer = document.getElementById("messages");
const messageInput = document.getElementById("message-input");
const welcomeMessage = document.getElementById("welcome-message");

async function sendMessage() {
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    if (isStreaming) return;
    const message = messageInput.value.trim();

    if (!message) return;
    isStreaming = true;
    messageInput.value = "";
    try {
        const response = await fetch("/chat/stream", {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message,
                conversation_id: conversationId
            })
        });


        if (response.status === 401) {
            alert("Session expired. Redirecting to login...")
            window.location.href = "/login";
            return;
        }

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        addMessage("user", message);
        await readStream(response);
        loadConversations();
    }
    catch(error) {
        alert("Couldn't reach server.");
        console.error(error);
    }
    finally {
        isStreaming = false;
    }
}

async function readStream(response) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    let buffer = "";

    const aiContent = addMessage("assistant", "");

    while(true) {
        const {value, done} = await reader.read();
        if(done) break;

        buffer += decoder.decode(value, {stream:true});
        const events = buffer.split("\n\n");
        buffer = events.pop();


        for(const eventString of events) {
            if(!eventString.startsWith("data:")) continue;

            const raw = eventString.slice(6);
            let event;
            try {
                event = JSON.parse(raw);
            }
            catch {
                continue;
            }


            switch(event.type) {
                case "conversation":
                    conversationId = event.id;
                    sessionStorage.setItem("conversation_id", conversationId);
                    break;

                case "token":
                    aiContent.textContent += event.content;
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    break;

                case "error":
                    aiContent.textContent += "\n[Error] " + event.message;
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;

                    break;

                case "done":
                    return;
            }
        }
    }
}

// ====Conversation======
async function loadConversations() {
    let response;
    try {
        response = await fetch("/chat/conversations", { credentials: "include" });
    } catch (error) {
        console.error("Couldn't load conversation list", error);
        return;
    }

    if (response.status === 401) {
        window.location.href = "/login";
        return;
    }

    if (!response.ok) {
        console.error("Failed to load conversations", response.status);
        return;
    }

    const conversations = await response.json();
    renderConversationList(conversations);
}

//render conversation list
function renderConversationList(conversations) {
    if (!chatList) return;

    chatList.innerHTML = "";

    const sorted = [...conversations].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    for (const convo of sorted) {
        const item = document.createElement("div");
        item.classList.add("chat-item");
        item.dataset.id = convo.id;

        if (convo.id === conversationId) {
            item.classList.add("active");
        }

        const title = document.createElement("div");
        title.classList.add("chat-title");
        title.textContent = convo.title || "Untitled conversation";

        const moreButton = document.createElement("button");
        moreButton.classList.add("more-button");
        moreButton.textContent = "...";

        moreButton.addEventListener("click", (event) => {
            event.stopPropagation();
            const existingMenu = document.querySelector(".conversation-menu");
            if (existingMenu) {
                existingMenu.remove();
            }
            const menu = document.createElement("div");
            menu.classList.add("conversation-menu");

            const deleteButton = document.createElement("button");
            deleteButton.textContent = "Delete";

            deleteButton.addEventListener("click", async (event) => {
                event.stopPropagation();
                try {
                    await deleteConversation(convo.id);
                    item.remove();
                    if (conversationId === convo.id) {
                        conversationId = null;
                        messagesContainer.innerHTML = "";
                    }
                } catch (error) {
                    console.error("Error deleting conversation:", error);
                    alert("Failed to delete conversation.");
                }
                menu.remove();
            });

            menu.appendChild(deleteButton);
            item.appendChild(menu);
        });

        item.appendChild(title);
        item.appendChild(moreButton);

        item.addEventListener("click", () => openConversation(convo.id));

        chatList.appendChild(item);
    }
}

//Open a specific conversation
async function openConversation(id) {
    let response;
    try {
        response = await fetch(`/chat/conversations/${id}`, { credentials: "include" });
    } catch (error) {
        console.error("Couldn't open conversation", error);
        return;
    }

    if (response.status === 401) {
        window.location.href = "/login";
        return;
    }

    if (!response.ok) {
        console.error("Failed to open conversation", response.status);
        return;
    }

    const conversation = await response.json();
    conversationId = conversation.id;
    sessionStorage.setItem("conversation_id", conversationId);

    messagesContainer.innerHTML = "";
    for (const message of conversation.messages) {
        addMessage(message.role, message.content);
    }

    highlightActiveConversation();
}

//=====Other functions

//Add a new chat
function newChat(){
    conversationId = null;
    sessionStorage.removeItem("conversation_id");
    messagesContainer.innerHTML = "";
    highlightActiveConversation();
    window.location.reload();
}


//delete a conversation
async function deleteConversation(id) {
    const response = await fetch(`/chat/conversations/${id}`, {
        method: "DELETE",
        credentials: "include"
    });

    if (!response.ok) {
        throw new Error("Failed to delete conversation");
    }
}

//highlight selected conversation
function highlightActiveConversation() {
    if (!chatList) return;
    chatList.querySelectorAll(".chat-item").forEach((item) => {
        item.classList.toggle("active", item.dataset.id === conversationId);
    });
}

function addMessage(role,text) {
    const message = document.createElement("div");

    if (role === "user") {
        message.classList.add("user-message");
    } else if(role === "assistant"){
        message.classList.add("assistant-message");
    }

    message.textContent = text;
    messagesContainer.appendChild(message);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    return message;
}

//=====Trigger Events=======
messageInput.addEventListener("keydown",(event)=>{
    if(event.key==="Enter" && !event.shiftKey){
        event.preventDefault();
        sendMessage();
    }
});
document.getElementById("logout-button").addEventListener("click", async () => {
        await fetch("/auth/logout", {
            method: "POST",
            credentials: "include"
        });

        window.location.href = "/login";
    });

// ---------- Initial load ----------
loadConversations();
// Restore whatever conversation this tab was on before a refresh.
if (conversationId) {
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    openConversation(conversationId);
}
else{ //new conversation

}