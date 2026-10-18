import { createBrowserRouter, Navigate } from "react-router-dom";
import { AppShell } from "./components/layout/AppShell";
import { HomePage } from "./pages/HomePage";
import { SearchPage } from "./pages/SearchPage";
import { PapersPage } from "./pages/PapersPage";
import { PaperDetailPage } from "./pages/PaperDetailPage";
import { TopicsPage } from "./pages/TopicsPage";
import { ClusterDetailPage } from "./pages/ClusterDetailPage";
import { AnalyticsPage } from "./pages/AnalyticsPage";
import { RecommendationsPage } from "./pages/RecommendationsPage";
import { LibraryPage } from "./pages/LibraryPage";
import { EvaluationPage } from "./pages/EvaluationPage";
import { AnalysisPage } from "./pages/AnalysisPage";
import { AdminPage } from "./pages/AdminPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { NotFoundPage } from "./pages/NotFoundPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppShell />,
    children: [
      { index: true, element: <HomePage /> },
      { path: "search", element: <SearchPage /> },
      { path: "papers", element: <PapersPage /> },
      { path: "papers/:id", element: <PaperDetailPage /> },
      { path: "topics", element: <TopicsPage /> },
      { path: "topics/clusters/:clusterId", element: <ClusterDetailPage /> },
      { path: "analytics", element: <AnalyticsPage /> },
      { path: "recommendations/:paperId", element: <RecommendationsPage /> },
      { path: "library", element: <LibraryPage /> },
      { path: "evaluation", element: <EvaluationPage /> },
      { path: "analysis", element: <AnalysisPage /> },
      { path: "admin/ingestion", element: <AdminPage /> },
      { path: "admin", element: <Navigate to="/admin/ingestion" replace /> },
      { path: "login", element: <LoginPage /> },
      { path: "register", element: <RegisterPage /> },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);
