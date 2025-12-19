import React from 'react';
import Layout from '@theme/Layout';

export default function SignUp(): JSX.Element {
  return (
    <Layout
      title="Sign Up"
      description="Join NeuroBot Physical AI & Humanoid Robotics Textbook">

      {/* Sign Up Hero Section */}
      <div style={{
        background: 'linear-gradient(180deg, var(--neurobot-bg-primary) 0%, var(--neurobot-bg-secondary) 100%)',
        padding: '6rem 2rem',
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          fontFamily: 'var(--neurobot-font-serif)',
          fontSize: '15rem',
          fontWeight: 700,
          color: 'rgba(91, 126, 200, 0.03)',
          zIndex: 0,
          lineHeight: 1
        }}>
          ✨
        </div>

        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{
            display: 'inline-block',
            background: 'rgba(45, 53, 97, 0.3)',
            border: '1px solid var(--neurobot-accent-primary)',
            color: 'var(--neurobot-accent-primary)',
            fontFamily: 'var(--neurobot-font-sans)',
            fontSize: '0.875rem',
            fontWeight: 600,
            padding: '0.5rem 1.25rem',
            borderRadius: '20px',
            marginBottom: '1.5rem',
            textTransform: 'uppercase',
            letterSpacing: '0.05em'
          }}>
            Coming Soon
          </div>

          <h1 style={{
            fontFamily: 'var(--neurobot-font-serif)',
            fontSize: '3.5rem',
            fontWeight: 700,
            color: 'var(--neurobot-text-primary)',
            marginBottom: '1rem',
            lineHeight: 1.2
          }}>
            Join the <span style={{
              background: 'linear-gradient(135deg, #2d3561 0%, #5b7ec8 50%, #4a5f8f 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>NeuroBot</span> Community
          </h1>

          <p style={{
            fontFamily: 'var(--neurobot-font-sans)',
            fontSize: '1.25rem',
            color: 'var(--neurobot-text-tertiary)',
            maxWidth: '700px',
            margin: '0 auto 3rem',
            lineHeight: 1.6
          }}>
            Get exclusive access to advanced chapters, interactive labs, and personalized learning paths in Physical AI and Humanoid Robotics.
          </p>

          {/* Feature List */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '2rem',
            maxWidth: '900px',
            margin: '0 auto 3rem',
            textAlign: 'left'
          }}>
            {[
              { icon: '🎓', title: 'Premium Content', desc: 'Access advanced tutorials and exclusive chapters' },
              { icon: '🔬', title: 'Interactive Labs', desc: 'Hands-on projects with real robot simulations' },
              { icon: '👥', title: 'Community', desc: 'Connect with AI researchers and roboticists' },
              { icon: '📜', title: 'Certification', desc: 'Earn certificates upon course completion' }
            ].map((feature, i) => (
              <div key={i} style={{
                background: 'var(--neurobot-bg-tertiary)',
                border: '1px solid var(--neurobot-border-default)',
                borderLeft: '4px solid var(--neurobot-accent-primary)',
                borderRadius: '12px',
                padding: '1.5rem',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-4px)';
                e.currentTarget.style.boxShadow = '0 8px 24px var(--neurobot-shadow-sm)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}>
                <div style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>{feature.icon}</div>
                <h3 style={{
                  fontFamily: 'var(--neurobot-font-serif)',
                  fontSize: '1.125rem',
                  color: 'var(--neurobot-text-primary)',
                  marginBottom: '0.5rem'
                }}>{feature.title}</h3>
                <p style={{
                  fontSize: '0.9375rem',
                  color: 'var(--neurobot-text-tertiary)',
                  margin: 0,
                  lineHeight: 1.6
                }}>{feature.desc}</p>
              </div>
            ))}
          </div>

          {/* Signup Form Placeholder */}
          <div style={{
            background: 'var(--neurobot-bg-tertiary)',
            border: '1px solid var(--neurobot-border-accent)',
            borderRadius: '16px',
            padding: '3rem',
            maxWidth: '500px',
            margin: '0 auto',
            boxShadow: '0 16px 48px var(--neurobot-shadow-lg)'
          }}>
            <h2 style={{
              fontFamily: 'var(--neurobot-font-serif)',
              fontSize: '1.875rem',
              color: 'var(--neurobot-text-primary)',
              marginBottom: '1.5rem',
              textAlign: 'center'
            }}>
              Early Access Waitlist
            </h2>

            <p style={{
              color: 'var(--neurobot-text-tertiary)',
              textAlign: 'center',
              marginBottom: '2rem',
              lineHeight: 1.6
            }}>
              Sign-up functionality is coming soon! Meanwhile, explore our free comprehensive textbook and start your Physical AI journey today.
            </p>

            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '1rem'
            }}>
              <a
                href="/docs/chapter-1"
                style={{
                  background: 'linear-gradient(135deg, #2d3561 0%, #4a5f8f 100%)',
                  color: 'white',
                  fontFamily: 'var(--neurobot-font-serif)',
                  fontSize: '1rem',
                  fontWeight: 600,
                  padding: '1rem 2rem',
                  borderRadius: '8px',
                  textDecoration: 'none',
                  textAlign: 'center',
                  transition: 'all 0.3s ease',
                  boxShadow: '0 4px 12px rgba(45, 53, 97, 0.3)'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'scale(1.05)';
                  e.currentTarget.style.boxShadow = '0 6px 20px rgba(45, 53, 97, 0.5)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'scale(1)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(45, 53, 97, 0.3)';
                }}
              >
                Start Learning for Free
              </a>

              <a
                href="/"
                style={{
                  background: 'transparent',
                  color: 'var(--neurobot-accent-primary)',
                  fontFamily: 'var(--neurobot-font-serif)',
                  fontSize: '1rem',
                  fontWeight: 600,
                  padding: '1rem 2rem',
                  border: '2px solid var(--neurobot-accent-primary)',
                  borderRadius: '8px',
                  textDecoration: 'none',
                  textAlign: 'center',
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(91, 126, 200, 0.1)';
                  e.currentTarget.style.transform = 'scale(1.03)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.transform = 'scale(1)';
                }}
              >
                Back to Home
              </a>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
