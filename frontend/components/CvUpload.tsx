'use client';

import { useState } from 'react';

/**
 * CvUpload Component - HU 01 Frontend (5.1 Entrada)
 * Maneja la subida de CV y expectativas del candidato
 * Con resaltado en rojo para campos obligatorios faltantes
 */

interface CVUploadData {
  email: string;
  full_name: string;
  cv_text: string;
  expected_salary: number;
  work_modality: string;
  location: string;
}

interface FieldErrors {
  [key: string]: boolean;
}

interface CvUploadProps {
  onSuccess?: (candidateId: number) => void;
  onError?: (error: string) => void;
}

export default function CvUpload({ onSuccess, onError }: CvUploadProps) {
  const [formData, setFormData] = useState<CVUploadData>({
    email: '',
    full_name: '',
    cv_text: '',
    expected_salary: 0,
    work_modality: '',
    location: ''
  });
  
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'expected_salary' ? parseFloat(value) || 0 : value
    }));
    
    // Clear error when user starts typing (5.3 Salida - feedback visual)
    if (fieldErrors[name]) {
      setFieldErrors(prev => ({ ...prev, [name]: false }));
    }
  };

  const handleSubmit = async (data: CVUploadData) => {
    try {
      // 5.1 Entrada: Enviar datos al backend puerto 8001
      const response = await fetch('http://localhost:8001/api/candidates/upload_cv', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        
        // Resaltado en rojo - HU 01: marcar campos faltantes
        if (errorData.detail?.fields) {
          const errors: FieldErrors = {};
          errorData.detail.fields.forEach((field: string) => {
            errors[field] = true;
          });
          setFieldErrors(errors);
        }
        
        throw new Error(errorData.detail?.message || "Campos obligatorios faltantes");
      }
      
      // 5.3 Salida: Mostrar éxito
      const result = await response.json();
      setSuccess(true);
      setErrorMessage(null);
      onSuccess?.(result.id);
      
    } catch (err: any) {
      // Lógica de resaltado en rojo (HU 01)
      setErrorMessage(err.message);
      onError?.(err.message);
    }
  };

  const onFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setSuccess(false);
    setErrorMessage(null);
    
    await handleSubmit(formData);
    setLoading(false);
  };

  const getInputClass = (fieldName: string): string => {
    const baseClass = "w-full px-4 py-2 rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none";
    // Resaltado en rojo para campos con error (HU 01)
    return fieldErrors[fieldName] 
      ? `${baseClass} border-2 border-red-500 bg-red-50` 
      : `${baseClass} border border-gray-300`;
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-8 max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">Subir CV y Preferencias</h2>
      
      {/* 5.3 Salida: Mensaje de éxito */}
      {success && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-green-800 font-medium">CV registrado exitosamente.</p>
          <p className="text-green-600 text-sm mt-1">
            Tu perfil ha sido analizado por nuestra IA.
          </p>
        </div>
      )}
      
      {/* Error message display */}
      {errorMessage && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 font-medium">Error: {errorMessage}</p>
        </div>
      )}
      
      <form onSubmit={onFormSubmit} className="space-y-6">
        {/* Email */}
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
            Email <span className="text-red-500">*</span>
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className={getInputClass('email')}
            placeholder="tu@email.com"
          />
          {fieldErrors.email && (
            <p className="mt-1 text-sm text-red-600">Email es requerido</p>
          )}
        </div>
        
        {/* Nombre Completo */}
        <div>
          <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-1">
            Nombre Completo <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="full_name"
            name="full_name"
            value={formData.full_name}
            onChange={handleChange}
            className={getInputClass('full_name')}
            placeholder="Juan Pérez"
          />
          {fieldErrors.full_name && (
            <p className="mt-1 text-sm text-red-600">Nombre completo es requerido</p>
          )}
        </div>
        
        {/* CV Text */}
        <div>
          <label htmlFor="cv_text" className="block text-sm font-medium text-gray-700 mb-1">
            Contenido del CV <span className="text-red-500">*</span>
          </label>
          <textarea
            id="cv_text"
            name="cv_text"
            value={formData.cv_text}
            onChange={handleChange}
            rows={6}
            className={getInputClass('cv_text')}
            placeholder="Pega aquí el contenido de tu CV..."
          />
          {fieldErrors.cv_text && (
            <p className="mt-1 text-sm text-red-600">El contenido del CV es requerido</p>
          )}
        </div>
        
        {/* Salario Esperado */}
        <div>
          <label htmlFor="expected_salary" className="block text-sm font-medium text-gray-700 mb-1">
            Salario Esperado (USD) <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            id="expected_salary"
            name="expected_salary"
            value={formData.expected_salary || ''}
            onChange={handleChange}
            className={getInputClass('expected_salary')}
            placeholder="3000"
            min="0"
          />
          {fieldErrors.expected_salary && (
            <p className="mt-1 text-sm text-red-600">Salario esperado es requerido</p>
          )}
        </div>
        
        {/* Modalidad de Trabajo */}
        <div>
          <label htmlFor="work_modality" className="block text-sm font-medium text-gray-700 mb-1">
            Modalidad de Trabajo <span className="text-red-500">*</span>
          </label>
          <select
            id="work_modality"
            name="work_modality"
            value={formData.work_modality}
            onChange={handleChange}
            className={getInputClass('work_modality')}
          >
            <option value="">Selecciona una opción</option>
            <option value="remote">Remoto</option>
            <option value="hybrid">Híbrido</option>
            <option value="onsite">Presencial</option>
          </select>
          {fieldErrors.work_modality && (
            <p className="mt-1 text-sm text-red-600">Modalidad de trabajo es requerida</p>
          )}
        </div>
        
        {/* Ubicación */}
        <div>
          <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-1">
            Ubicación <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="location"
            name="location"
            value={formData.location}
            onChange={handleChange}
            className={getInputClass('location')}
            placeholder="Medellín, Colombia"
          />
          {fieldErrors.location && (
            <p className="mt-1 text-sm text-red-600">Ubicación es requerida</p>
          )}
        </div>
        
        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-primary-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Procesando...' : 'Enviar CV'}
        </button>
      </form>
    </div>
  );
}
