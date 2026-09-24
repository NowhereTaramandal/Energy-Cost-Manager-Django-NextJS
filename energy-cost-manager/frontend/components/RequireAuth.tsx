"use client";
import {useEffect} from "react";import {useRouter} from "next/navigation";import {useAuth} from "./AuthProvider";
export default function RequireAuth({children}:{children:React.ReactNode}){const{user,loading}=useAuth();const r=useRouter();useEffect(()=>{if(!loading&&!user)r.replace("/login")},[loading,user,r]);if(loading||!user)return <div className="p-10">Loading…</div>;return <>{children}</>}
