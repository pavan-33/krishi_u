import axios from 'axios';

const BASE_URL = 'http://localhost:8000/'; // Replace with your FastAPI backend URL

const axiosInstance = axios.create({
    baseURL: BASE_URL,
    timeout: 10000, // 10 seconds timeout
    headers: {
        'Content-Type': 'application/json',
    },
});

export default axiosInstance;
