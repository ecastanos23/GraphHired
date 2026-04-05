'use client';

import React, { useRef, useState, MouseEvent, ReactNode } from 'react';

interface ButtonProps {
  children: ReactNode;
  onClick?: () => void;
  className?: string;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
  glowColor?: string;
  backgroundColor?: string;
  textColor?: string;
  hoverTextColor?: string;
}

const HoverButton: React.FC<ButtonProps> = ({
  children,
  onClick,
  className = '',
  disabled = false,
  type = 'button',
  glowColor = '#00ffc3',
  backgroundColor = '#111827',
  textColor = '#ffffff',
  hoverTextColor = '#67e8f9',
}) => {
  const buttonRef = useRef<HTMLButtonElement>(null);
  const [glowPosition, setGlowPosition] = useState({ x: 50, y: 50 });
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseMove = (e: MouseEvent<HTMLButtonElement>) => {
    if (buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      setGlowPosition({ x, y });
    }
  };

  return (
    <button
      ref={buttonRef}
      onClick={onClick}
      disabled={disabled}
      type={type}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={[
        'relative inline-block overflow-hidden rounded-lg border-none px-8 py-4',
        'cursor-pointer text-xl font-semibold transition-colors duration-300',
        disabled ? 'cursor-not-allowed opacity-50' : '',
        className,
      ]
        .filter(Boolean)
        .join(' ')}
      style={{
        backgroundColor,
        color: isHovered ? hoverTextColor : textColor,
      }}
    >
      <div
        className={[
          'pointer-events-none absolute h-[200px] w-[200px] -translate-x-1/2 -translate-y-1/2 rounded-full opacity-50',
          'transition-transform duration-300 ease-out',
          isHovered ? 'scale-100' : 'scale-0',
        ].join(' ')}
        style={{
          left: `${glowPosition.x}px`,
          top: `${glowPosition.y}px`,
          background: `radial-gradient(circle, ${glowColor} 10%, transparent 70%)`,
          zIndex: 0,
        }}
      />
      <span className="relative z-10">{children}</span>
    </button>
  );
};

export { HoverButton };
