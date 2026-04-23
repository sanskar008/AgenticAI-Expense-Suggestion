import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { FaRobot, FaChartLine, FaWallet, FaBullseye } from 'react-icons/fa';
import './Analysis.css';

const Copilot = () => {
    const [prediction, setPrediction] = useState(null);
    const [budgets, setBudgets] = useState([]);
    const [loading, setLoading] = useState(true);

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

    useEffect(() => {
        const fetchData = async () => {
            try {
                const predRes = await axios.get('http://localhost:5000/api/predictions');
                const budgRes = await axios.get('http://localhost:5000/api/budgets');
                setPrediction(predRes.data.prediction);
                setBudgets(budgRes.data.budgets);
            } catch (error) {
                console.error("Error fetching copilot data", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) return <div>Loading Copilot Intelligence...</div>;

    return (
        <div className="copilot-container">
            <h2><FaRobot /> AI Financial Copilot</h2>
            
            <div className="copilot-grid">
                {/* Prediction Card */}
                <div className="stat-card prediction-card">
                    <h3><FaChartLine /> Forecast</h3>
                    <div className="prediction-value">
                        <span className="label">End-of-Month Est:</span>
                        <span className="value">₹{prediction?.predicted_total?.toLocaleString()}</span>
                    </div>
                    <div className="prediction-chart">
                        <ResponsiveContainer width="100%" height={200}>
                            <PieChart>
                                <Pie
                                    data={Object.entries(prediction?.category_forecast || {}).map(([name, value]) => ({ name, value }))}
                                    cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value"
                                >
                                    {Object.entries(prediction?.category_forecast || {}).map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Budget Card */}
                <div className="stat-card budget-card">
                    <h3><FaWallet /> Budget vs Actual</h3>
                    <div className="budget-list">
                        {budgets.map((b, i) => (
                            <div key={i} className="budget-item">
                                <div className="budget-info">
                                    <span>{b.category}</span>
                                    <span>{Math.round(b.percent)}%</span>
                                </div>
                                <div className="progress-bar">
                                    <div 
                                        className={`progress-fill ${b.percent > 100 ? 'critical' : b.percent > 80 ? 'warning' : 'good'}`} 
                                        style={{ width: `${Math.min(b.percent, 100)}%` }}
                                    ></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Copilot;
