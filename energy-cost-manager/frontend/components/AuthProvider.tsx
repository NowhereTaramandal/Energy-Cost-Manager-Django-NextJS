"use client";
import {createContext,useContext,useEffect,useState} from "react";
import api from "@/lib/api";
type User={id:string;email:string;username:string;first_name:string;last_name:string};
const C=createContext<{user:User|null;loading:boolean;login:(e:string,p:string)=>Promise<void>;logout:()=>void;refresh:()=>Promise<void>}>({user:null,loading:true,login:async()=>{},logout:()=>{},refresh:async()=>{}});
export function AuthProvider({children}:{children:React.ReactNode}){const[user,setUser]=useState<User|null>(null);const[loading,setLoading]=useState(true);const refresh=async()=>{try{const r=await api.get("/auth/me/");setUser(r.data);}catch{setUser(null);}finally{setLoading(false)}};useEffect(()=>{if(localStorage.getItem("access"))refresh();else setLoading(false)},[]);const login=async(email:string,password:string)=>{const r=await api.post("/auth/token/",{email,password});localStorage.setItem("access",r.data.access);localStorage.setItem("refresh",r.data.refresh);await refresh()};const logout=()=>{localStorage.removeItem("access");localStorage.removeItem("refresh");setUser(null);window.location.href="/login"};return <C.Provider value={{user,loading,login,logout,refresh}}>{children}</C.Provider>}
export const useAuth=()=>useContext(C);
