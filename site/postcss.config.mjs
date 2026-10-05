import rfs from 'rfs';

export default {
  plugins: [
    rfs({
      baseValue: '1rem',
      breakpoint: 1280,
    }),
  ],
};
