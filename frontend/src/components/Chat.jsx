import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { FaPaperPlane, FaRobot, FaUser } from 'react-icons/fa';
import './Chat.css';

const Chat = () => {
    const [messages, setMessages] = useState([
        { role: 'assistant', text: "Hello! I'm your AI Financial Copilot. How can I help you today?" }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg = input;
        setInput('');
        setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
        setLoading(true);

        try {
            const res = await axios.post('http://localhost:5000/api/chat', { message: userMsg });
            setMessages(prev => [...prev, { role: 'assistant', text: res.data.response }]);
        } catch (error) {
            setMessages(prev => [...prev, { role: 'assistant', text: "Sorry, I'm having trouble connecting right now." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chat-widget">
            <div className="chat-header">
                <h3><FaRobot /> AI Copilot Chat</h3>
            </div>
            <div className="chat-messages">
                {messages.map((m, i) => (
                    <div key={i} className={`message ${m.role}`}>
                        <div className="icon">{m.role === 'assistant' ? <FaRobot /> : <FaUser />}</div>
                        <div className="text">{m.text}</div>
                    </div>
                ))}
                {loading && <div className="message assistant"><div className="text">Thinking...</div></div>}
                <div ref={messagesEndRef} />
            </div>
            <form className="chat-input" onSubmit={handleSend}>
                <input 
                    value={input} 
                    onChange={(e) => setInput(e.target.value)} 
                    placeholder="Ask me anything... (e.g. 'Where did I overspend?')"
                />
                <button type="submit" disabled={loading}><FaPaperPlane /></button>
            </form>
        </div>
    );
};

export default Chat;
