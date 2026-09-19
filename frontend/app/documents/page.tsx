"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface Document {
  id: number;
  document_type: string;
  title: string;
  number: string | null;
  status: string;
  created_at?: string;
}

export default function DocumentsPage() {
  const router = useRouter();

  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");

  // Форма загрузки
  const [docType, setDocType] = useState("Положение");
  const [title, setTitle] = useState("");
  const [number, setNumber] = useState("");
  const [file, setFile] = useState<File | null>(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  async function loadDocuments() {
    const token = localStorage.getItem("access_token");

    if (!token) {
      router.push("/login");
      return;
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/documents/`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        if (response.status === 401) {
          localStorage.removeItem("access_token");
          router.push("/login");
          return;
        }
        throw new Error("Не удалось загрузить документы");
      }

      const data = await response.json();
      setDocuments(data);
    } catch (error) {
      console.error(error);
      setMessage("Ошибка загрузки списка документов");
    } finally {
      setLoading(false);
    }
  }

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();

    if (!file || !title) {
      setMessage("Укажите название и выберите файл");
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
    formData.append("document_type", docType);
    formData.append("title", title);
    formData.append("number", number);
    formData.append("file", file);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/documents/upload`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.detail || "Ошибка загрузки"
        );
      }

      setMessage("Документ успешно загружен");
      
      // Очистка формы
      setTitle("");
      setNumber("");
      setFile(null);
      
      // Перезагрузка списка
      await loadDocuments();
    } catch (error) {
      console.error(error);
      setMessage(
        error instanceof Error ? error.message : "Ошибка загрузки"
      );
    } finally {
      setUploading(false);
    }
  }

  return (
    <main style={styles.container}>
      <div style={styles.header}>
        <div>
          <h1 style={{ marginBottom: 5 }}>Школьные документы</h1>
          <p style={styles.subtitle}>
            Локальные нормативные акты и внутренние документы
          </p>
        </div>
        <button
          onClick={() => router.push("/dashboard")}
          style={styles.secondaryButton}
        >
          В кабинет
        </button>
      </div>

      {/* Форма загрузки */}
      <section style={styles.card}>
        <h2>Загрузить новый документ</h2>
        <form onSubmit={handleUpload} style={styles.form}>
          <div style={styles.formRow}>
            <label style={styles.label}>
              Тип документа
              <select
                value={docType}
                onChange={(e) => setDocType(e.target.value)}
                style={styles.input}
                required
              >
                <option value="Положение">Положение</option>
                <option value="Приказ">Приказ</option>
                <option value="Инструкция">Инструкция</option>
                <option value="Протокол">Протокол</option>
                <option value="Другое">Другое</option>
              </select>
            </label>

            <label style={styles.label}>
              Название
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Например: Положение о текущем контроле"
                style={styles.input}
                required
              />
            </label>

            <label style={styles.label}>
              Номер (необязательно)
              <input
                type="text"
                value={number}
                onChange={(e) => setNumber(e.target.value)}
                placeholder="Например: 123-ОД"
                style={styles.input}
              />
            </label>
          </div>

          <label style={styles.label}>
            Файл (DOCX, PDF)
            <input
              type="file"
              onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
              style={styles.input}
              accept=".doc,.docx,.pdf"
              required
            />
          </label>

          <div style={styles.actions}>
            <button
              type="submit"
              disabled={uploading}
              style={{
                ...styles.primaryButton,
                opacity: uploading ? 0.7 : 1,
              }}
            >
              {uploading ? "Загрузка..." : "Загрузить документ"}
            </button>
          </div>
        </form>
        
        {message && (
          <p style={{ 
            marginTop: 15, 
            color: message.includes("ошиб") ? "#d32f2f" : "#2e7d32",
            fontWeight: 500 
          }}>
            {message}
          </p>
        )}
      </section>

      {/* Список документов */}
      <section style={{ ...styles.card, marginTop: 30 }}>
        <h2>Мои документы</h2>
        
        {loading ? (
          <p>Загрузка списка...</p>
        ) : documents.length === 0 ? (
          <p style={{ color: "#666" }}>
            У вас пока нет загруженных документов.
          </p>
        ) : (
          <div style={styles.tableWrapper}>
            <table style={styles.table}>
              <thead>
                <tr style={styles.trHead}>
                  <th style={styles.th}>Тип</th>
                  <th style={styles.th}>Название</th>
                  <th style={styles.th}>Номер</th>
                  <th style={styles.th}>Статус</th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc) => (
                  <tr key={doc.id} style={styles.tr}>
                    <td style={styles.td}>{doc.document_type}</td>
                    <td style={{ ...styles.td, fontWeight: 500 }}>{doc.title}</td>
                    <td style={styles.td}>{doc.number || "-"}</td>
                    <td style={styles.td}>
                      <span style={styles.statusBadge}>{doc.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    maxWidth: 1000,
    margin: "40px auto",
    padding: 20,
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 30,
  },
  subtitle: {
    color: "#666",
  },
  card: {
    background: "white",
    padding: 30,
    borderRadius: 12,
    boxShadow: "0 2px 10px rgba(0,0,0,0.05)",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: 20,
    marginTop: 20,
  },
  formRow: {
    display: "grid",
    gridTemplateColumns: "1fr 2fr 1fr",
    gap: 20,
  },
  label: {
    display: "flex",
    flexDirection: "column",
    fontSize: 14,
    fontWeight: 500,
    gap: 8,
  },
  input: {
    padding: "10px 12px",
    borderRadius: 6,
    border: "1px solid #ddd",
    fontSize: 14,
  },
  actions: {
    display: "flex",
    alignItems: "center",
    gap: 20,
    marginTop: 10,
  },
  primaryButton: {
    padding: "12px 24px",
    border: "none",
    borderRadius: 8,
    background: "#2563eb",
    color: "white",
    fontWeight: 600,
    cursor: "pointer",
  },
  secondaryButton: {
    padding: "10px 20px",
    border: "1px solid #ccc",
    borderRadius: 8,
    background: "white",
    cursor: "pointer",
  },
  tableWrapper: {
    overflowX: "auto",
    marginTop: 20,
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    fontSize: 14,
  },
  trHead: {
    borderBottom: "2px solid #eee",
    textAlign: "left",
  },
  th: {
    padding: "12px 16px",
    fontWeight: 600,
    color: "#555",
  },
  tr: {
    borderBottom: "1px solid #eee",
  },
  td: {
    padding: "12px 16px",
  },
  statusBadge: {
    display: "inline-block",
    padding: "4px 8px",
    borderRadius: 4,
    background: "#e0f2fe",
    color: "#0369a1",
    fontSize: 12,
    fontWeight: 600,
  },
};