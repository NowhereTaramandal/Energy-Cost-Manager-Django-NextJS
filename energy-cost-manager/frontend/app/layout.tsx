
import "./globals.css";
import { AuthProvider } from "@/components/AuthProvider";

export const metadata = {
    title: "Energy Cost Manager",
    description: "Analyse electricity usage and compare plans",
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body>
                <AuthProvider>
                    {children}
                </AuthProvider>
            </body>
        </html>
    );
}
