"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface NormativeDoc {
  id: number;
  title: string;
  doc_number: string | null;
  source_name: string | null;
  status: string;
  is_important: boolean;
  created_at: string;
}

export default function AdminNormativePage() {
  const router = useRouter();
  const [docs, setDocs] = useState<NormativeDoc[]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  // Форма загрузки
  const [title, setTitle] = useState("");
  const [docNumber, setDocNumber] = useState("");
  const [sourceName, setSourceName] = useState("");
  const [officialUrl, setOfficialUrl] = useState("");
  const [summary, setSummary] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    // Проверка токена (можно добавить проверку на супер-админа)
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }
    loadDocs();
  }, [router]);

  async function loadDocs() {
    const token = localStorage.getItem("access_token");
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/normative/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setDocs(data);
      } else {
        setMessage("Ошибка загрузки списка документов");
      }
    } catch (e) {
      console.error(e);
      setMessage("Ошибка сети");
    } finally {
      setLoading(false);
    }
  }

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!title) {
      setMessage("Введите название документа");
      return;
    }

    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    setUploading(true);
    setMessage("");

    const formData = new FormData();
    formData.append("title", title);
    if (docNumber) formData.append("doc_number", docNumber);
    if (sourceName) formData.append("source_name", sourceName);
    if (officialUrl) formData.append("official_url", officialUrl);
    if (summary) formData.append("summary", summary);
    if (file) formData.append("file", file);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/normative/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Ошибка загрузки");
      }

      setMessage("Документ успешно загружен!");
      setTitle("");
      setDocNumber("");
      setSourceName("");
      setOfficialUrl("");
      setSummary("");
      setFile(null);
      loadDocs();
    } catch (err: any) {
      setMessage(err.message || "Ошибка при загрузке");
    } finally {
      setUploading(false);
    }
  }

  return (
    <main style={styles.container}>
      <div style={styles.header}>
        <h1>Администрирование: Нормативные документы</h1>
        <button onClick={() => router.push("/dashboard")} style={styles.btnSecondary}>
          В кабинет
        </button>
      </div>

      {/* Форма загрузки */}
      <section style={styles.card}>
        <h2>Загрузить новый нормативный документ</h2>
        <form onSubmit={handleUpload} style={styles.form}>
          <div style={styles.row}>
            <label style={styles.label}>
              Название *
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                style={styles.input}
                required
              />
            </label>
            <label style={styles.label}>
              Номер
              <input
                value={docNumber}
                onChange={(e) => setDocNumber(e.target.value)}
                style={styles.input}
              />
            </label>
          </div>

          <div style={styles.row}>
            <label style={styles.label}>
              Источник (напр. Минпросвещения)
              <input
                value={sourceName}
                onChange={(e) => setSourceName(e.target.value)}
                style={styles.input}
              />
            </label>
            <label style={styles.label}>
              Ссылка на источник
              <input
                value={officialUrl}
                onChange={(e) => setOfficialUrl(e.target.value)}
                style={styles.input}
                placeholder="https://..."
              />
            </label>
          </div>

          <label style={styles.label}>
            Краткое описание (для поста в VK)
            <textarea
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              style={{ ...styles.input, minHeight: 80 }}
              placeholder="Коротко о сути изменений..."
            />
          </label>

          <label style={styles.label}>
            Файл (DOCX, PDF)
            <input
              type="file"
              onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
              style={styles.input}
              accept=".pdf,.doc,.docx"
            />
          </label>

          <button
            type="submit"
            disabled={uploading}
            style={{ ...styles.btnPrimary, opacity: uploading ? 0.7 : 1 }}
          >
            {uploading ? "Загрузка..." : "Загрузить документ"}
          </button>
        </form>
        {message && (
          <p style={{ marginTop: 15, color: message.includes("Ошибка") ? "#d32f2f" : "#2e7d32" }}>
            {message}
          </p>
        )}
      </section>

      {/* Список документов */}
      <section style={{ ...styles.card, marginTop: 30 }}>
        <h2>Список документов</h2>
        {loading ? (
          <p>Загрузка...</p>
        ) : docs.length === 0 ? (
          <p>Документов пока нет.</p>
        ) : (
          <table style={styles.table}>
            <thead>
              <tr style={styles.trHead}>
                <th style={styles.th}>Дата</th>
                <th style={styles.th}>Название</th>
                <th style={styles.th}>Источник</th>
                <th style={styles.th}>Статус</th>
                <th style={styles.th}>Действия</th>
              </tr>
            </thead>
            <tbody>
              {docs.map((doc) => (
                <tr key={doc.id} style={styles.tr}>
                  <td style={styles.td}>{new Date(doc.created_at).toLocaleDateString()}</td>
                  <td style={styles.td}>
                    <strong>{doc.title}</strong>
                    {doc.doc_number && <div style={{ fontSize: 12, color: "#666" }}>№ {doc.doc_number}</div>}
                  </td>
                  <td style={styles.td}>{doc.source_name || "-"}</td>
                  <td style={styles.td}>
                    <span style={styles.badge}>{doc.status}</span>
                  </td>
                  <td style={styles.td}>
                    <button
                      onClick={() => router.push(`/admin/normative/${doc.id}`)}
                      style={styles.btnSmall}
                    >
                      Редактировать / VK
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </main>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: { maxWidth: 1000, margin: "40px auto", padding: 20 },
  header: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 30 },
  card: { background: "white", padding: 30, borderRadius: 12, boxShadow: "0 2px 10px rgba(0,0,0,0.05)" },
  form: { display: "flex", flexDirection: "column", gap: 20, marginTop: 20 },
  row: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 },
  label: { display: "flex", flexDirection: "column", fontSize: 14, fontWeight: 500, gap: 8 },
  input: { padding: "10px 12px", borderRadius: 6, border: "1px solid #ddd", fontSize: 14 },
  btnPrimary: { padding: "12px 24px", border: "none", borderRadius: 8, background: "#2563eb", color: "white", fontWeight: 600, cursor: "pointer", alignSelf: "start" },
  btnSecondary: { padding: "10px 20px", border: "1px solid #ccc", borderRadius: 8, background: "white", cursor: "pointer" },
  btnSmall: { padding: "6px 12px", fontSize: 12, border: "1px solid #ddd", borderRadius: 4, background: "white", cursor: "pointer" },
  table: { width: "100%", borderCollapse: "collapse", marginTop: 20 },
  trHead: { borderBottom: "2px solid #eee", textAlign: "left" },
  th: { padding: "12px 16px", fontWeight: 600, color: "#555" },
  tr: { borderBottom: "1px solid #eee" },
  td: { padding: "12px 16px" },
  badge: { display: "inline-block", padding: "4px 8px", borderRadius: 4, background: "#e0f2fe", color: "#0369a1", fontSize: 12, fontWeight: 600 },
};