'use client';

import { useState } from 'react';
import { useApi } from '@/hooks/useApi';

interface FormData {
  email: string;
  full_name: string;
  cv_text: string;
  expected_salary: string;
  work_modality: string;
  location: string;
}

interface FormErrors {
  [key: string]: boolean;
}

interface CandidateResponse {
  id: number;
  email: string;
  full_name: string;
}

export default function UploadPage() {
  const { post, loading, error } = useApi();
  const [formData, setFormData] = useState<FormData>({
    email: '',
    full_name: '',
    cv_text: '',
    expected_salary: '',
    work_modality: '',
    location: ''
  });
  const [formErrors, setFormErrors] = useState<FormErrors>({});
  const [success, setSuccess] = useState(false);
  const [candidateId, setCandidateId] = useState<number | null>(null);

  const validateForm = (): boolean => {
    const errors: FormErrors = {};
    
    if (!formData.email) errors.email = true;
    if (!formData.full_name || formData.full_name.length < 2) errors.full_name = true;
    if (!formData.cv_text || formData.cv_text.length < 10) errors.cv_text = true;
    if (!formData.expected_salary || parseFloat(formData.expected_salary) < 0) errors.expected_salary = true;
    if (!formData.work_modality) errors.work_modality = true;
    if (!formData.location) errors.location = true;
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccess(false);
    
    if (!validateForm()) {
      return;
    }

    try {
      const response = await post<CandidateResponse>('/api/candidates/upload-cv', {
        ...formData,
        expected_salary: parseFloat(formData.expected_salary)
      });
      
      if (response) {
        setSuccess(true);
        setCandidateId(response.id);
      }
    } catch (err) {
      console.error('Error uploading CV:', err);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (formErrors[name]) {
      setFormErrors(prev => ({ ...prev, [name]: false }));
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-xl shadow-md p-8">
        <h1 className="text-2xl font-bold mb-6">Subir CV y Preferencias</h1>
        
        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-800 font-medium">✓ CV registrado exitosamente!</p>
            <p className="text-green-600 text-sm mt-1">
              Tu perfil ha sido analizado. 
              <a href={`/dashboard?candidateId=${candidateId}`} className="underline ml-1">
                Ver vacantes recomendadas
              </a>
            </p>
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">Error: {error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Email */}
          <div>
            <label htmlFor="email" className="form-label">
              Email <span className="text-red-500">*</span>
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className={`form-input ${formErrors.email ? 'form-error border-2 border-red-500' : 'border border-gray-300'}`}
              placeholder="tu@email.com"
            />
            {formErrors.email && (
              <p className="mt-1 text-sm text-red-600">Email es requerido</p>
            )}
          </div>

          {/* Full Name */}
          <div>
            <label htmlFor="full_name" className="form-label">
              Nombre Completo <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="full_name"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              className={`form-input ${formErrors.full_name ? 'form-error border-2 border-red-500' : 'border border-gray-300'}`}
              placeholder="Juan Pérez"
            />
            {formErrors.full_name && (
              <p className="mt-1 text-sm text-red-600">Nombre completo es requerido (mínimo 2 caracteres)</p>
            )}
          </div>

          {/* CV Text */}
          <div>
            <label htmlFor="cv_text" className="form-label">
              Contenido del CV <span className="text-red-500">*</span>
            </label>
            <textarea
              id="cv_text"
              name="cv_text"
              rows={8}
              value={formData.cv_text}
              onChange={handleChange}
              className={`form-input ${formErrors.cv_text ? 'form-error border-2 border-red-500' : 'border border-gray-300'}`}
              placeholder="Pega aquí el contenido de tu CV o escribe un resumen de tu experiencia, habilidades y formación..."
            />
            {formErrors.cv_text && (
              <p className="mt-1 text-sm text-red-600">CV es requerido (mínimo 10 caracteres)</p>
            )}
          </div>

          {/* Expected Salary */}
          <div>
            <label htmlFor="expected_salary" className="form-label">
              Salario Esperado (USD anual) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              id="expected_salary"
              name="expected_salary"
              value={formData.expected_salary}
              onChange={handleChange}
              className={`form-input ${formErrors.expected_salary ? 'form-error border-2 border-red-500' : 'border border-gray-300'}`}
              placeholder="60000"
              min="0"
            />
            {formErrors.expected_salary && (
              <p className="mt-1 text-sm text-red-600">Salario esperado es requerido</p>
            )}
          </div>

          {/* Work Modality */}
          <div>
            <label htmlFor="work_modality" className="form-label">
              Modalidad de Trabajo <span className="text-red-500">*</span>
            </label>
            <select
              id="work_modality"
              name="work_modality"
              value={formData.work_modality}
              onChange={handleChange}
              className={`form-input ${formErrors.work_modality ? 'form-error border-2 border-red-500' : 'border border-gray-300'}`}
            >
              <option value="">Seleccionar...</option>
              <option value="remote">Remoto</option>
              <option value="hybrid">Híbrido</option>
              <option value="onsite">Presencial</option>
            </select>
            {formErrors.work_modality && (
              <p className="mt-1 text-sm text-red-600">Modalidad es requerida</p>
            )}
          </div>

          {/* Location */}
          <div>
            <label htmlFor="location" className="form-label">
              Ubicación <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="location"
              name="location"
              value={formData.location}
              onChange={handleChange}
              className={`form-input ${formErrors.location ? 'form-error border-2 border-red-500' : 'border border-gray-300'}`}
              placeholder="Bogotá, Colombia"
            />
            {formErrors.location && (
              <p className="mt-1 text-sm text-red-600">Ubicación es requerida</p>
            )}
          </div>

          <div className="pt-4">
            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary py-3 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Procesando...' : 'Subir CV y Analizar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
