import axios from "axios";
const api=axios.create({baseURL:process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000/api"});
api.interceptors.request.use((config)=>{if(typeof window!=="undefined"){const t=localStorage.getItem("access");if(t) config.headers.Authorization=`Bearer ${t}`;}return config;});
api.interceptors.response.use(r=>r,async(error)=>{const original=error.config;if(error.response?.status===401 && !original?._retry && typeof window!=="undefined"){original._retry=true;const refresh=localStorage.getItem("refresh");if(refresh){try{const r=await axios.post(`${api.defaults.baseURL}/auth/token/refresh/`,{refresh});localStorage.setItem("access",r.data.access);original.headers.Authorization=`Bearer ${r.data.access}`;return api(original);}catch{localStorage.removeItem("access");localStorage.removeItem("refresh");}}}return Promise.reject(error);});
export default api;
