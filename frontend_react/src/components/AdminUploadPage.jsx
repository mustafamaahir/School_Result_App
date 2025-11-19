import AdminLayout from "../components/AdminLayout";
import UploadResults from "../components/UploadResults";
import ProtectedRoute from "./ProtectedRoute";

export default function AdminUploadPage() {
  return (
    <AdminLayout>
      <UploadResults />
    </AdminLayout>
  );
}