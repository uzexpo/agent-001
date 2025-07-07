import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';
import { colors } from './colors';

// Новый компонент страницы Agent AI
function AgentAIPage() {
  return (
    <div className="agent-ai-page">
      <header className="agent-ai-header">
        <div className="zerro-logo-title">
          <span className="zerro-logo">⚡Z</span>
          <span className="zerro-title">Zerro</span>
        </div>
        <h2 className="agent-ai-subtitle">Возможности AI-агентов</h2>
        <p className="agent-ai-desc">Всё, что нужно для создания мощного AI-ассистента для вашего бизнеса и жизни.</p>
      </header>
      <section className="agent-ai-features">
        <div className="feature-card">
          <span className="feature-icon">⚙️</span>
          <h3>Гибкая настройка</h3>
          <p>Настройте инструкции и поведение агентов под ваши задачи и стиль.</p>
        </div>
        <div className="feature-card">
          <span className="feature-icon">💬</span>
          <h3>Интеграция с Telegram</h3>
          <p>Лёгкое подключение к Telegram и другим мессенджерам.</p>
        </div>
        <div className="feature-card">
          <span className="feature-icon">📊</span>
          <h3>Продвинутая аналитика</h3>
          <p>Анализируйте диалоги, отслеживайте эффективность агентов.</p>
        </div>
        <div className="feature-card">
          <span className="feature-icon">⚡</span>
          <h3>Поддержка моделей OpenAI</h3>
          <p>Используйте GPT-3.5/4 и другие LLM для естественных ответов.</p>
        </div>
        <div className="feature-card">
          <span className="feature-icon">🧪</span>
          <h3>Эмулятор для тестирования</h3>
          <p>Тестируйте агентов в удобном эмуляторе перед запуском.</p>
        </div>
        <div className="feature-card">
          <span className="feature-icon">🔒</span>
          <h3>Безопасность и надёжность</h3>
          <p>Ваши данные и ключи API защищены.</p>
        </div>
      </section>
      <section className="agent-ai-faq">
        <h2>Часто задаваемые вопросы</h2>
        <div className="faq-list">
          <details>
            <summary>Как начать использовать Zerro?</summary>
            <p>Зарегистрируйтесь, настройте агентов и интеграции — и начните автоматизировать задачи!</p>
          </details>
          <details>
            <summary>Нужны ли навыки программирования?</summary>
            <p>Нет, всё настраивается через удобный интерфейс.</p>
          </details>
          <details>
            <summary>Можно ли интегрировать агентов в другие платформы?</summary>
            <p>Да, доступны интеграции с Telegram, Google, облачными сервисами и API.</p>
          </details>
          <details>
            <summary>Какие модели ИИ поддерживаются?</summary>
            <p>GPT-3.5, GPT-4, локальные LLM и другие.</p>
          </details>
          <details>
            <summary>Есть ли ограничения в бесплатном плане?</summary>
            <p>Бесплатный план — для знакомства и личных задач, есть лимиты на количество агентов и сообщений.</p>
          </details>
        </div>
      </section>
    </div>
  );
}

function App() {
    const [query, setQuery] = useState('');
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [currentView, setCurrentView] = useState('blocks');
    const [responseData, setResponseData] = useState(null);
    const [isOnline, setIsOnline] = useState(false);
    const [status, setStatus] = useState('Agents ready');
    const messagesEndRef = useRef(null);

    useEffect(() => {
        const intervalId = setInterval(() => {
            checkHealth();
            fetchLatestAnswer();
            fetchScreenshot();
        }, 3000);
        return () => clearInterval(intervalId);
    }, [messages]);

    const checkHealth = async () => {
        try {
            await axios.get('http://127.0.0.1:8000/health');
            setIsOnline(true);
            console.log('System is online');
        } catch {
            setIsOnline(false);
            console.log('System is offline');
        }
    };

    const fetchScreenshot = async () => {
        try {
            const timestamp = new Date().getTime();
            const res = await axios.get(`http://127.0.0.1:8000/screenshots/updated_screen.png?timestamp=${timestamp}`, {
                responseType: 'blob'
            });
            console.log('Screenshot fetched successfully');
            const imageUrl = URL.createObjectURL(res.data);
            setResponseData((prev) => {
                if (prev?.screenshot && prev.screenshot !== 'placeholder.png') {
                    URL.revokeObjectURL(prev.screenshot);
                }
                return {
                    ...prev,
                    screenshot: imageUrl,
                    screenshotTimestamp: new Date().getTime()
                };
            });
        } catch (err) {
            console.error('Error fetching screenshot:', err);
            setResponseData((prev) => ({
                ...prev,
                screenshot: 'placeholder.png',
                screenshotTimestamp: new Date().getTime()
            }));
        }
    };

    const normalizeAnswer = (answer) => {
        return answer
            .trim()
            .toLowerCase()
            .replace(/\s+/g, ' ')
            .replace(/[.,!?]/g, '')
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const fetchLatestAnswer = async () => {
        try {
            const res = await axios.get('http://127.0.0.1:8000/latest_answer');
            const data = res.data;

            updateData(data);
            if (!data.answer || data.answer.trim() === '') {
                return;
            }
            const normalizedNewAnswer = normalizeAnswer(data.answer);
            const answerExists = messages.some(
                (msg) => normalizeAnswer(msg.content) === normalizedNewAnswer
            );
            if (!answerExists) {
                setMessages((prev) => [
                    ...prev,
                    {
                        type: 'agent',
                        content: data.answer,
                        agentName: data.agent_name,
                        status: data.status,
                        uid: data.uid,
                    },
                ]);
                setStatus(data.status);
                scrollToBottom();
            } else {
                console.log('Duplicate answer detected, skipping:', data.answer);
            }
        } catch (error) {
            console.error('Error fetching latest answer:', error);
        }
    };

    const updateData = (data) => {
        setResponseData((prev) => ({
            ...prev,
            blocks: data.blocks || prev.blocks || null,
            done: data.done,
            answer: data.answer,
            agent_name: data.agent_name,
            status: data.status,
            uid: data.uid,
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        checkHealth();
        if (!query.trim()) {
            console.log('Empty query');
            return;
        }
        setMessages((prev) => [...prev, { type: 'user', content: query }]);
        setIsLoading(true);
        setError(null);

        try {
            console.log('Sending query:', query);
            setQuery('waiting for response...');
            const res = await axios.post('http://127.0.0.1:8000/query', {
                query,
                tts_enabled: false
            });
            setQuery('Enter your query...');
            console.log('Response:', res.data);
            const data = res.data;
            updateData(data);
        } catch (err) {
            console.error('Error:', err);
            setError('Failed to process query.');
            setMessages((prev) => [
                ...prev,
                { type: 'error', content: 'Error: Unable to get a response.' },
            ]);
        } finally {
            console.log('Query completed');
            setIsLoading(false);
            setQuery('');
        }
    };

    const handleGetScreenshot = async () => {
        try {
            setCurrentView('screenshot');
        } catch (err) {
            setError('Browser not in use');
        }
    };

    return (
        <div className="app">
            <header className="header">
                <h1 onClick={() => setCurrentView('blocks')}>AgenticSeek</h1>
                <nav>
                  <button onClick={() => setCurrentView('agent-ai')}>Agent AI</button>
                  {/* другие кнопки меню */}
                </nav>
            </header>
            <main className="main">
                {currentView === 'agent-ai' ? (
                  <AgentAIPage />
                ) : (
                  <div className="app-sections">
                    <div className="chat-section">
                        <h2>Chat Interface</h2>
                        <div className="messages">
                            {messages.length === 0 ? (
                                <p className="placeholder">No messages yet. Type below to start!</p>
                            ) : (
                                messages.map((msg, index) => (
                                    <div
                                        key={index}
                                        className={`message ${
                                            msg.type === 'user'
                                                ? 'user-message'
                                                : msg.type === 'agent'
                                                ? 'agent-message'
                                                : 'error-message'
                                        }`}
                                    >
                                        {msg.type === 'agent' && (
                                            <span className="agent-name">{msg.agentName}</span>
                                        )}
                                        <p>{msg.content}</p>
                                    </div>
                                ))
                            )}
                            <div ref={messagesEndRef} />
                        </div>
                        {isOnline && <div className="loading-animation">{status}</div>}
                        {!isLoading && !isOnline && <p className="loading-animation">System offline. Deploy backend first.</p>}
                        <form onSubmit={handleSubmit} className="input-form">
                            <input
                                type="text"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                placeholder="Type your query..."
                                disabled={isLoading}
                            />
                            <button type="submit" disabled={isLoading}>
                                Send
                            </button>
                        </form>
                    </div>

                    <div className="computer-section">
                        <h2>Computer View</h2>
                        <div className="view-selector">
                            <button
                                className={currentView === 'blocks' ? 'active' : ''}
                                onClick={() => setCurrentView('blocks')}
                            >
                                Editor View
                            </button>
                            <button
                                className={currentView === 'screenshot' ? 'active' : ''}
                                onClick={responseData?.screenshot ? () => setCurrentView('screenshot') : handleGetScreenshot}
                            >
                                Browser View
                            </button>
                        </div>
                        <div className="content">
                            {error && <p className="error">{error}</p>}
                            {currentView === 'blocks' ? (
                                <div className="blocks">
                                    {responseData && responseData.blocks && Object.values(responseData.blocks).length > 0 ? (
                                        Object.values(responseData.blocks).map((block, index) => (
                                            <div key={index} className="block">
                                                <p className="block-tool">Tool: {block.tool_type}</p>
                                                <pre>{block.block}</pre>
                                                <p className="block-feedback">Feedback: {block.feedback}</p>
                                                <p className="block-success">
                                                    Success: {block.success ? 'Yes' : 'No'}
                                                </p>
                                            </div>
                                        ))
                                    ) : (
                                        <div className="block">
                                            <p className="block-tool">Tool: No tool in use</p>
                                            <pre>No file opened</pre>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <div className="screenshot">
                                    <img
                                        src={responseData?.screenshot || 'placeholder.png'}
                                        alt="Screenshot"
                                        onError={(e) => {
                                            e.target.src = 'placeholder.png';
                                            console.error('Failed to load screenshot');
                                        }}
                                        key={responseData?.screenshotTimestamp || 'default'}
                                    />
                                </div>
                            )}
                        </div>
                    </div>
                  </div>
                )}
            </main>
        </div>
    );
}

export default App;
