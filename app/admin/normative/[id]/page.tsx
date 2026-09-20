"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";

export default function EditNormativePage() {
  const router = useRouter();
  const params = useParams();
  // Получаем ID из URL
  const docId = params.id as string;

  const [loading, setLoading] = useState(false);
  const [sendingVk, setSendingVk] = useState(false);
  const [message, setMessage] = useState("");
  
  // Данные формы
  const [title, setTitle] = useState("Загрузка...");
  const [summary, setSummary] = useState("");
  const [vkMessage, setVkMessage] = useState("");

  useEffect(() => {
    // В будущем здесь будет запрос к API: GET /api/normative/{id}
    // Сейчас просто эмулируем загрузку
    setTitle(`Документ #${docId}`);
    setSummary("Описание для теста...");
    setVkMessage(`Внимание! Обновлен документ #${docId}. Ознакомьтесь с изменениями.`);
  }, [docId]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    
    // Эмуляция сохранения
    setTimeout(() => {
      setMessage("Изменения сохранены (демо-режим)");
      setLoading(false);
    }, 800);
  }

  async function handleSendVk() {
    if (!vkMessage) {
      setMessage("Введите текст поста");
      return;
    }

    setSendingVk(true);
    setMessage("");

    try {
      // 1. Создаем черновик
      const token = localStorage.getItem("access_token");
      const draftRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/normative/${docId}/vk-draft`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ post_message: vkMessage }),
      });

      if (!draftRes.ok) throw new Error("Ошибка создания черновика");
      
      const draftData = await draftRes.json();
      
      // 2. Отправляем пост (используем ID созданного черновика)
      const sendRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/normative/vk-send/${draftData.id}`, {
         method: "POST",
         headers: { Authorization: `Bearer ${token}` },
      });
      
      if (sendRes.ok) {
        setMessage("✅ Пост успешно отправлен в VK!");
      } else {
        setMessage("Черновик создан, но отправка не удалась.");
      }
    } catch (err: any) {
      setMessage("❌ " + (err.message || "Ошибка при работе с VK"));
    } finally {
      setSendingVk(false);
    }
  }

  return (
    <main style={styles.container}>
      <div style={styles.header}>
        <h1>Редактирование: {title}</h1>
        <button onClick={() => router.back()} style={styles.btnSecondary}>Назад</button>
      </div>

      {message && (
        <div style={{
          marginBottom: 20, 
          padding: "10px 15px", 
          borderRadius: 6, 
          background: message.includes("✅") ? "#d1fae5" : (message.includes("❌") ? "#fee2e2" : "#dbeafe"),
          color: message.includes("✅") ? "#065f46" : (message.includes("❌") ? "#991b1b" : "#1e40af")
        }}>
          {message}
        </div>
      )}

      <section style={styles.card}>
        <h2>Данные документа</h2>
        <form onSubmit={handleSave} style={styles.form}>
          <label style={styles.label}>
            Название
            <input 
              value={title} 
              onChange={(e) => setTitle(e.target.value)} 
              style={styles.input} 
            />
          </label>
          
          <label style={styles.label}>
            Краткое описание (суть изменений)
            <textarea 
              value={summary} 
              onChange={(e) => setSummary(e.target.value)} 
              style={{...styles.input, minHeight: 80}} 
            />
          </label>

          <button type="submit" disabled={loading} style={styles.btnPrimary}>
            {loading ? "Сохранение..." : "Сохранить изменения"}
          </button>
        </form>
      </section>

      <section style={{...styles.card, marginTop: 30}}>
        <h2>Публикация ВКонтакте</h2>
        <p style={{fontSize: 14, color: "#666", marginBottom: 15}}>
          Текст сообщения будет опубликован в группе школы.
        </p>
        
        <label style={styles.label}>
            Текст поста
            <textarea 
              value={vkMessage} 
              onChange={(e) => setVkMessage(e.target.value)} 
              style={{...styles.input, minHeight: 100, fontFamily: "inherit"}} 
              placeholder="Уважаемые коллеги! Изменился приказ..."
            />
        </label>

        <div style={{marginTop: 20}}>
            <button 
              onClick={handleSendVk} 
              disabled={sendingVk || !vkMessage} 
              style={{
                ...styles.btnVk, 
                opacity: sendingVk || !vkMessage ? 0.6 : 1,
                cursor: sendingVk || !vkMessage ? 'not-allowed' : 'pointer'
              }}
            >
              {sendingVk ? "Отправка..." : "🚀 Опубликовать в VK"}
            </button>
        </div>
      </section>
    </main>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: { maxWidth: 800, margin: "40px auto", padding: 20 },
  header: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 30 },
  card: { background: "white", padding: 30, borderRadius: 12, boxShadow: "0 2px 10px rgba(0,0,0,0.05)" },
  form: { display: "flex", flexDirection: "column", gap: 20, marginTop: 20 },
  label: { display: "flex", flexDirection: "column", fontSize: 14, fontWeight: 500, gap: 8 },
  input: { padding: "10px 12px", borderRadius: 6, border: "1px solid #ddd", fontSize: 14, fontFamily: "inherit" },
  btnPrimary: { padding: "12px 24px", background: "#2563eb", color: "white", border: "none", borderRadius: 8, cursor: "pointer", fontWeight: 600, alignSelf: "start" },
  btnSecondary: { padding: "10px 20px", background: "white", border: "1px solid #ccc", borderRadius: 8, cursor: "pointer" },
  btnVk: { padding: "12px 24px", background: "#0077FF", color: "white", border: "none", borderRadius: 8, cursor: "pointer", fontWeight: 600, fontSize: 15 },
};