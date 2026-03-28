-- Representative SQL for Nigeria's 774 LGAs
-- This facilitates the 3-tier geographical hierarchy: State -> LGA -> Neighborhood

CREATE TABLE IF NOT EXISTS lgas (
    id SERIAL PRIMARY KEY,
    state TEXT NOT NULL,
    lga_name TEXT NOT NULL,
    tier INTEGER DEFAULT 4 -- T1-T4 logic
);

INSERT INTO lgas (state, lga_name, tier) VALUES 
('Lagos', 'Ikeja', 1),
('Lagos', 'Eti-Osa', 1),
('Lagos', 'Alimosho', 2),
('FCT', 'Abuja Municipal', 1),
('FCT', 'Gwagwalada', 2),
('Kaduna', 'Chikun', 2),
('Kaduna', 'Kaduna South', 2),
('Rivers', 'Obio-Akpor', 2),
('Rivers', 'Port Harcourt City', 2),
('Oyo', 'Ibadan North', 2),
('Kano', 'Nassarawa', 2);

-- Note: In a production environment, this would contain all 774 LGAs.
